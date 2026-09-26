import json
import os
from pathlib import Path
from typing import Any, Dict, List, Optional
from pydantic import BaseModel

from src.core.config import settings

class MCPServerConfig(BaseModel):
    name: str
    command: Optional[str] = None
    args: List[str] = []
    env: Dict[str, str] = {}
    server_url: Optional[str] = None

class MCPManager:
    """
    Manages Model Context Protocol (MCP) server definitions and connections.
    """
    def __init__(self, config_path: Optional[Path] = None):
        self.config_path = config_path or settings.mcp_config_file
        self.servers: Dict[str, MCPServerConfig] = {}
        self.load_servers()

    def load_servers(self) -> None:
        self.servers.clear()
        if not self.config_path.exists():
            return

        try:
            with open(self.config_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                server_dict = data.get("mcpServers", {})
                for name, cfg in server_dict.items():
                    self.servers[name] = MCPServerConfig(
                        name=name,
                        command=cfg.get("command"),
                        args=cfg.get("args", []),
                        env=cfg.get("env", {}),
                        server_url=cfg.get("serverUrl")
                    )
        except Exception:
            pass

    def list_servers(self) -> List[MCPServerConfig]:
        return list(self.servers.values())

mcp_manager = MCPManager()
