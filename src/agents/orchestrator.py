import subprocess
import time
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.core.config import settings
from src.core.telemetry import tracer
from src.governance.hook_engine import hook_engine, HookDecision
from src.memory.manager import memory_manager
from src.skills.registry import skill_registry
from src.agents.prompts import build_system_prompt

class ExecutionResult(BaseModel):
    success: bool
    output: str
    error: Optional[str] = None
    hook_decision: Optional[str] = None
    blocked_reason: Optional[str] = None

class AgentOrchestrator:
    """
    Coordinates the end-to-end agent execution loop:
    Context Assembly -> Governance Interception -> Execution -> Post-Processing -> Telemetry
    """
    def __init__(self):
        self.memory = memory_manager
        self.skills = skill_registry
        self.hooks = hook_engine

    def prepare_context(self, user_query: str) -> str:
        """Assembles tiered context into a prompt."""
        rules = self.memory.get_l2_rules()
        available_skills = self.skills.list_available_skills()
        
        # Recall L4 memories matching query keywords
        memories = self.memory.query_l4_memory(query="", limit=3)
        recalled_str = "\n".join([f"- [{m['category']}] {m['content']}" for m in memories])

        return build_system_prompt(
            rules=rules,
            available_skills=available_skills,
            recalled_memory=recalled_str
        )

    def execute_command_with_governance(self, command: str, confirm_callback=None) -> ExecutionResult:
        """
        Executes a shell command through the full governance pipeline.
        """
        start_time = time.time()
        tool_name = "run_command"
        args = {"CommandLine": command}

        # 1. PreToolUse Governance Gate
        hook_decision: HookDecision = self.hooks.run_pre_tool_hook(tool_name, args)

        if hook_decision.decision == "deny":
            duration_ms = (time.time() - start_time) * 1000
            tracer.record_step(
                "execution_blocked",
                tool_name,
                inputs=args,
                error=hook_decision.reason,
                duration_ms=duration_ms
            )
            return ExecutionResult(
                success=False,
                output="",
                error=f"Action blocked by policy: {hook_decision.reason}",
                hook_decision="deny",
                blocked_reason=hook_decision.reason
            )

        if hook_decision.decision in ["ask", "force_ask"]:
            allowed = True
            if confirm_callback:
                allowed = confirm_callback(command, hook_decision.reason or "Confirmation required")
            if not allowed:
                return ExecutionResult(
                    success=False,
                    output="",
                    error="Operator declined confirmation",
                    hook_decision="denied_by_operator",
                    blocked_reason="Operator declined confirmation"
                )

        # 2. Tool Execution
        try:
            cwd = settings.project_root
            proc = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(cwd),
                timeout=30
            )
            output = proc.stdout
            error = proc.stderr if proc.returncode != 0 else None
            success = proc.returncode == 0
        except subprocess.TimeoutExpired:
            success = False
            output = ""
            error = "Execution timed out after 30 seconds"
        except Exception as e:
            success = False
            output = ""
            error = str(e)

        # 3. PostToolUse Hook
        self.hooks.run_post_tool_hook(tool_name, args, output)

        duration_ms = (time.time() - start_time) * 1000
        tracer.record_step(
            "command_execution",
            tool_name,
            inputs=args,
            outputs={"stdout": output, "stderr": error},
            error=error,
            duration_ms=duration_ms
        )

        return ExecutionResult(
            success=success,
            output=output,
            error=error,
            hook_decision=hook_decision.decision
        )

orchestrator = AgentOrchestrator()
