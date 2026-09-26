import json
import re
import subprocess
import time
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.core.config import settings
from src.core.telemetry import tracer

class HookDecision(BaseModel):
    decision: str  # "allow", "deny", "ask", "force_ask"
    reason: Optional[str] = None
    overwrite: Optional[Dict[str, Any]] = None

class HookEngine:
    """
    Executes lifecycle hooks defined in hooks.json.
    Enforces deterministic boundaries around tool calls and invocation lifecycles.
    """
    def __init__(self, hooks_path: Optional[Path] = None):
        self.hooks_path = hooks_path or settings.hooks_file
        self.config = self._load_config()

    def _load_config(self) -> Dict[str, Any]:
        if not self.hooks_path.exists():
            return {}
        try:
            with open(self.hooks_path, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            tracer.record_step("hook_config_error", "load_hooks", {}, error=str(e))
            return {}

    def run_pre_tool_hook(self, tool_name: str, args: Dict[str, Any], step_idx: int = 0) -> HookDecision:
        """
        Executes PreToolUse handlers.
        Returns: HookDecision with 'allow', 'deny', or 'ask'.
        """
        start_time = time.time()
        payload = {
            "toolCall": {
                "name": tool_name,
                "args": args
            },
            "stepIdx": step_idx,
            "workspacePaths": [str(settings.project_root)]
        }

        # Iterate through hook definitions
        for hook_group_name, hook_spec in self.config.items():
            if not hook_spec.get("enabled", True):
                continue

            for handler_group in hook_spec.get("PreToolUse", []):
                matcher = handler_group.get("matcher", "")
                if matcher and not self._matches(tool_name, matcher):
                    continue

                for handler in handler_group.get("hooks", []):
                    cmd = handler.get("command")
                    timeout = handler.get("timeout", 15)

                    if not cmd:
                        continue

                    # Execute hook command
                    res = self._execute_hook_process(cmd, payload, timeout)
                    duration_ms = (time.time() - start_time) * 1000

                    tracer.record_step(
                        "pre_tool_hook",
                        hook_group_name,
                        inputs=payload,
                        outputs=res,
                        duration_ms=duration_ms
                    )

                    decision = res.get("decision", "allow")
                    if decision in ["deny", "ask", "force_ask"]:
                        return HookDecision(
                            decision=decision,
                            reason=res.get("reason", "Action stopped by hook"),
                            overwrite=res.get("overwrite")
                        )

        return HookDecision(decision="allow", reason="All hooks passed")

    def run_post_tool_hook(self, tool_name: str, args: Dict[str, Any], result: Any, step_idx: int = 0) -> None:
        """
        Executes PostToolUse handlers (e.g. linters, secret redactors).
        """
        start_time = time.time()
        payload = {
            "toolCall": {"name": tool_name, "args": args},
            "result": str(result),
            "stepIdx": step_idx
        }

        for hook_group_name, hook_spec in self.config.items():
            if not hook_spec.get("enabled", True):
                continue

            for handler_group in hook_spec.get("PostToolUse", []):
                matcher = handler_group.get("matcher", "")
                if matcher and not self._matches(tool_name, matcher):
                    continue

                for handler in handler_group.get("hooks", []):
                    cmd = handler.get("command")
                    timeout = handler.get("timeout", 15)
                    if cmd:
                        res = self._execute_hook_process(cmd, payload, timeout)
                        duration_ms = (time.time() - start_time) * 1000
                        tracer.record_step(
                            "post_tool_hook",
                            hook_group_name,
                            inputs=payload,
                            outputs=res,
                            duration_ms=duration_ms
                        )

    def _matches(self, tool_name: str, matcher: str) -> bool:
        if matcher in ["*", ""]:
            return True
        return bool(re.search(matcher, tool_name))

    def _execute_hook_process(self, command: str, input_data: Dict[str, Any], timeout: int) -> Dict[str, Any]:
        try:
            cwd = settings.project_root
            process = subprocess.run(
                command,
                input=json.dumps(input_data),
                text=True,
                capture_output=True,
                shell=True,
                cwd=str(cwd),
                timeout=timeout
            )
            stdout = process.stdout.strip()
            if stdout:
                try:
                    return json.loads(stdout)
                except json.JSONDecodeError:
                    return {"decision": "deny", "reason": f"Invalid JSON returned by hook: {stdout}"}
            if process.returncode != 0:
                stderr = process.stderr.strip()
                return {"decision": "deny", "reason": f"Hook failed with exit code {process.returncode}: {stderr}"}
            return {"decision": "allow"}
        except subprocess.TimeoutExpired:
            return {"decision": "deny", "reason": f"Hook timed out after {timeout}s"}
        except Exception as e:
            return {"decision": "deny", "reason": f"Hook execution failed: {e}"}

hook_engine = HookEngine()
