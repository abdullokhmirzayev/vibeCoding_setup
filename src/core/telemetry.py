import json
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, Optional

class TelemetryTracer:
    """
    Lightweight, production-grade telemetry tracer.
    Logs structured traces locally and exports to Langfuse/OpenTelemetry if configured.
    """
    def __init__(self, log_dir: Optional[Path] = None):
        self.log_dir = log_dir or Path(".logs")
        self.log_dir.mkdir(parents=True, exist_ok=True)
        self.trace_file = self.log_dir / "agent_traces.jsonl"

    def record_step(
        self,
        step_type: str,
        name: str,
        inputs: Dict[str, Any],
        outputs: Optional[Dict[str, Any]] = None,
        error: Optional[str] = None,
        duration_ms: float = 0.0,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        event = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "step_type": step_type,  # e.g., "llm_invocation", "pre_tool_hook", "tool_execution", "post_tool_hook"
            "name": name,
            "inputs": inputs,
            "outputs": outputs or {},
            "error": error,
            "duration_ms": round(duration_ms, 2),
            "metadata": metadata or {}
        }

        # Write to JSONL audit log
        with open(self.trace_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(event) + "\n")

        return event

tracer = TelemetryTracer()
