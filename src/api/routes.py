from typing import Any, Dict, List, Optional
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from src.core.config import settings
from src.core.llm import llm_client
from src.governance.hook_engine import hook_engine
from src.skills.registry import skill_registry
from src.memory.manager import memory_manager
from src.tools.mcp_client import mcp_manager
from src.agents.orchestrator import orchestrator

router = APIRouter(prefix="/api/v1")

# --- Schemas ---
class CommandCheckRequest(BaseModel):
    command: str = Field(..., json_schema_extra={"example": "git status"})

class CommandCheckResponse(BaseModel):
    command: str
    decision: str
    reason: Optional[str] = None

class AgentRunRequest(BaseModel):
    query: str = Field(..., json_schema_extra={"example": "Review current codebase and inspect git status"})
    execute_safe_commands: bool = Field(default=False)

class MemoryCreateRequest(BaseModel):
    content: str
    category: str = "general"
    metadata: Optional[Dict[str, Any]] = None

# --- Routes ---

@router.post("/governance/check", response_model=CommandCheckResponse, tags=["Governance"])
def check_command(req: CommandCheckRequest):
    """
    Evaluates a proposed command against deterministic PreToolUse governance hooks.
    """
    decision = hook_engine.run_pre_tool_hook("run_command", {"CommandLine": req.command})
    return CommandCheckResponse(
        command=req.command,
        decision=decision.decision,
        reason=decision.reason
    )

@router.get("/skills", tags=["Skills"])
def list_skills():
    """
    Lists all available skills with lightweight metadata (Progressive Disclosure).
    """
    skill_registry.refresh()
    skills = skill_registry.list_available_skills()
    return [
        {
            "name": s.name,
            "description": s.description,
            "has_scripts": s.has_scripts,
            "has_references": s.has_references
        }
        for s in skills
    ]

@router.get("/skills/{name}", tags=["Skills"])
def get_skill_detail(name: str):
    """
    Loads full runbook content and script paths for a specific skill on demand.
    """
    detail = skill_registry.get_skill_detail(name)
    if not detail:
        raise HTTPException(status_code=404, detail=f"Skill '{name}' not found")
    return {
        "name": detail.metadata.name,
        "description": detail.metadata.description,
        "content": detail.content,
        "scripts": [s.name for s in detail.scripts],
        "references": [r.name for r in detail.references]
    }

@router.get("/memory", tags=["Memory"])
def list_memories(query: str = "", limit: int = 10):
    """
    Queries L4 persistent long-term memory.
    """
    return memory_manager.query_l4_memory(query=query, limit=limit)

@router.post("/memory", tags=["Memory"])
def add_memory(req: MemoryCreateRequest):
    """
    Stores an insight or user preference in L4 memory.
    """
    mem_id = memory_manager.add_l4_memory(
        content=req.content,
        category=req.category,
        metadata=req.metadata
    )
    return {"status": "created", "id": mem_id, "content": req.content}

@router.get("/tools/mcp", tags=["Tools"])
def list_mcp_servers():
    """
    Lists configured Model Context Protocol (MCP) servers.
    """
    mcp_manager.load_servers()
    return mcp_manager.list_servers()

@router.post("/agent/run", tags=["Agent"])
def run_agent(req: AgentRunRequest):
    """
    Executes an autonomous agent cycle:
    Context Assembly -> LLM Completion -> Optional Command Execution -> Telemetry
    """
    system_prompt = orchestrator.prepare_context(req.query)
    llm_resp = llm_client.complete(system_prompt=system_prompt, user_prompt=req.query)

    exec_result = None
    if req.execute_safe_commands:
        exec_result = orchestrator.execute_command_with_governance("git status --short")

    return {
        "query": req.query,
        "llm_response": llm_resp.content,
        "model_used": llm_resp.model,
        "provider": llm_resp.provider,
        "command_executed": exec_result.model_dump() if exec_result else None
    }
