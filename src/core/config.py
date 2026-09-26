import os
from pathlib import Path
from pydantic import BaseModel, Field

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent

class Settings(BaseModel):
    project_root: Path = PROJECT_ROOT
    agents_dir: Path = PROJECT_ROOT / ".agents"
    rules_file: Path = PROJECT_ROOT / "AGENTS.md"
    hooks_file: Path = PROJECT_ROOT / ".agents" / "hooks.json"
    mcp_config_file: Path = PROJECT_ROOT / ".agents" / "mcp_config.json"
    skills_dir: Path = PROJECT_ROOT / ".agents" / "skills"

    # Model Provider Settings
    model_provider: str = Field(default_factory=lambda: os.getenv("MODEL_PROVIDER", "gemini"))
    model_name: str = Field(default_factory=lambda: os.getenv("MODEL_NAME", "gemini-2.5-flash"))
    api_key: str = Field(default_factory=lambda: os.getenv("GEMINI_API_KEY") or os.getenv("OPENAI_API_KEY", ""))

    # Observability
    langfuse_public_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY", ""))
    langfuse_secret_key: str = Field(default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY", ""))
    langfuse_host: str = Field(default_factory=lambda: os.getenv("LANGFUSE_HOST", "http://localhost:3000"))

    # Governance
    governance_strict_mode: bool = Field(default_factory=lambda: os.getenv("GOVERNANCE_STRICT_MODE", "true").lower() == "true")
    human_in_the_loop: bool = Field(default_factory=lambda: os.getenv("HUMAN_IN_THE_LOOP", "true").lower() == "true")

settings = Settings()
