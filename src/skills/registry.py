import re
from pathlib import Path
from typing import Dict, List, Optional
import yaml

from src.core.config import settings
from src.skills.models import SkillDetail, SkillMetadata

class SkillRegistry:
    """
    Manages skills with Progressive Disclosure.
    Discovers skills, extracts lightweight metadata for prompts,
    and loads full runbooks and scripts on-demand.
    """
    def __init__(self, skills_dir: Optional[Path] = None):
        self.skills_dir = skills_dir or settings.skills_dir
        self._skills_cache: Dict[str, SkillMetadata] = {}
        self.refresh()

    def refresh(self) -> None:
        """Scan skills directory and build metadata catalog."""
        self._skills_cache.clear()
        if not self.skills_dir.exists():
            return

        for skill_folder in self.skills_dir.iterdir():
            if not skill_folder.is_dir():
                continue

            skill_md = skill_folder / "SKILL.md"
            if not skill_md.exists():
                continue

            metadata = self._parse_metadata(skill_folder, skill_md)
            if metadata:
                self._skills_cache[metadata.name] = metadata

    def list_available_skills(self) -> List[SkillMetadata]:
        """Returns lightweight metadata for all discovered skills (saving context budget)."""
        return list(self._skills_cache.values())

    def get_skill_detail(self, name: str) -> Optional[SkillDetail]:
        """Loads full skill content, executable scripts, and references on demand."""
        metadata = self._skills_cache.get(name)
        if not metadata:
            return None

        skill_folder = metadata.path
        skill_md = skill_folder / "SKILL.md"

        try:
            raw_text = skill_md.read_text(encoding="utf-8")
            # Strip YAML frontmatter
            content = re.sub(r"^---\n.*?\n---\n", "", raw_text, flags=re.DOTALL).strip()

            scripts = []
            scripts_dir = skill_folder / "scripts"
            if scripts_dir.exists():
                scripts = [f for f in scripts_dir.iterdir() if f.is_file()]

            references = []
            ref_dir = skill_folder / "references"
            if ref_dir.exists():
                references = [f for f in ref_dir.iterdir() if f.is_file()]

            return SkillDetail(
                metadata=metadata,
                content=content,
                scripts=scripts,
                references=references
            )
        except Exception:
            return None

    def _parse_metadata(self, folder: Path, skill_md: Path) -> Optional[SkillMetadata]:
        try:
            text = skill_md.read_text(encoding="utf-8")
            frontmatter_match = re.match(r"^---\n(.*?)\n---", text, re.DOTALL)
            if not frontmatter_match:
                return None

            data = yaml.safe_load(frontmatter_match.group(1))
            name = data.get("name", folder.name)
            desc = data.get("description", "").strip()

            has_scripts = (folder / "scripts").exists()
            has_refs = (folder / "references").exists()

            return SkillMetadata(
                name=name,
                description=desc,
                path=folder,
                has_scripts=has_scripts,
                has_references=has_refs
            )
        except Exception:
            return None

skill_registry = SkillRegistry()
