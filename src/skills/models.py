from pathlib import Path
from typing import List, Optional
from pydantic import BaseModel

class SkillMetadata(BaseModel):
    name: str
    description: str
    path: Path
    has_scripts: bool = False
    has_references: bool = False

class SkillDetail(BaseModel):
    metadata: SkillMetadata
    content: str
    scripts: List[Path] = []
    references: List[Path] = []
