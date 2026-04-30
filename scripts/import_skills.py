#!/usr/bin/env python3
"""Create local ATLAS skill templates from a curated repository list.

The importer is intentionally conservative. It creates attribution-ready
template directories and can optionally fetch one source file from GitHub using
Python stdlib only.
"""

from __future__ import annotations

import argparse
import json
import logging
import os
from dataclasses import asdict, dataclass
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from urllib.error import URLError
from urllib.request import Request, urlopen


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

PROJECT_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = PROJECT_ROOT / "skills"


@dataclass
class SkillMetadata:
    name: str
    category: str
    source_org: str
    source_repo: str
    source_path: str
    imported_at: str
    github_url: str


class SkillsImporter:
    """Imports configured skill templates into `skills/<category>/<name>/`."""

    SKILLS_CONFIG = {
        "official-openai": [
            ("openai/openai-python", ""),
            ("openai/openai-node", ""),
            ("openai/cookbook", ""),
        ],
        "official-anthropic": [
            ("anthropics/anthropic-sdk-python", ""),
            ("anthropics/anthropic-sdk-js", ""),
            ("anthropics/anthropic-cookbook", ""),
        ],
        "official-google": [
            ("google/generative-ai-python", ""),
            ("google-gemini/cookbook", ""),
        ],
        "official-vercel": [
            ("vercel/next.js", "examples"),
            ("vercel/ai", "examples"),
        ],
        "official-cloudflare": [
            ("cloudflare/workers-sdk", "templates"),
            ("cloudflare/workers-ai", "examples"),
        ],
    }

    def __init__(self, dry_run: bool = False, github_token: Optional[str] = None) -> None:
        self.dry_run = dry_run
        self.github_token = github_token or os.getenv("GITHUB_TOKEN")
        self.imported_skills: List[SkillMetadata] = []
        self.failed_skills: List[Tuple[str, str, str]] = []

    def _fetch_github_file(self, owner_repo: str, path: str) -> Optional[str]:
        if not path:
            return None

        for branch in ("main", "master"):
            url = f"https://raw.githubusercontent.com/{owner_repo}/{branch}/{path}"
            headers = {"User-Agent": "atlas-skills-importer"}
            if self.github_token:
                headers["Authorization"] = f"Bearer {self.github_token}"
            try:
                request = Request(url, headers=headers)
                with urlopen(request, timeout=10) as response:
                    if response.status == 200:
                        return response.read().decode("utf-8")
            except URLError as exc:
                logger.debug("Could not fetch %s: %s", url, exc)
        return None

    def _create_skill_directory(self, category: str, skill_name: str, files: Dict[str, str]) -> bool:
        skill_dir = SKILLS_DIR / category / skill_name
        if self.dry_run:
            logger.info("[DRY RUN] Would create %s", skill_dir)
            return True

        try:
            skill_dir.mkdir(parents=True, exist_ok=True)
            for filename, content in files.items():
                (skill_dir / filename).write_text(content, encoding="utf-8")
            logger.info("Created skill: %s/%s", category, skill_name)
            return True
        except OSError as exc:
            logger.error("Failed to create %s: %s", skill_dir, exc)
            return False

    def _create_skill_template(
        self, skill_name: str, source_org: str, source_repo: str, github_url: str
    ) -> Dict[str, str]:
        readable_name = skill_name.replace("-", " ").replace("_", " ").title()
        readme = f"""# {readable_name}

## Purpose

Describe when an agent should use this imported skill.

## Source

- Repository: [{source_repo}]({github_url})
- Source organization: {source_org}

## Instructions

1. Review the source repository before using this skill in production.
2. Add concrete triggers, inputs, and outputs.
3. Remove placeholders before publishing.

## Compatibility

OpenClaw, Claude Code, Codex CLI, Qwen Code CLI.
"""
        manifest = {
            "name": skill_name,
            "version": "0.1.0",
            "description": f"Template for {readable_name}",
            "compatibility": ["openclaw", "claude-code", "codex-cli", "qwen-code"],
            "source": {"org": source_org, "repo": source_repo, "url": github_url},
            "dependencies": [],
        }
        return {"README.md": readme, "manifest.json": json.dumps(manifest, indent=2)}

    def import_skill(
        self,
        category: str,
        skill_name: str,
        source_org: str,
        source_repo: str,
        source_path: str = "",
    ) -> bool:
        github_url = f"https://github.com/{source_repo}"
        logger.info("Importing %s/%s from %s", category, skill_name, source_repo)
        files = self._create_skill_template(skill_name, source_org, source_repo, github_url)

        content = self._fetch_github_file(source_repo, source_path)
        if content:
            files[Path(source_path).name] = content

        success = self._create_skill_directory(category, skill_name, files)
        if success:
            self.imported_skills.append(
                SkillMetadata(
                    name=skill_name,
                    category=category,
                    source_org=source_org,
                    source_repo=source_repo,
                    source_path=source_path or "template",
                    imported_at=datetime.utcnow().isoformat(),
                    github_url=github_url,
                )
            )
        else:
            self.failed_skills.append((category, skill_name, source_org))
        return success

    def import_all(self) -> None:
        for category in self.SKILLS_CONFIG:
            self.import_category(category, print_summary=False)
        self._print_summary()

    def import_category(self, category: str, print_summary: bool = True) -> None:
        skills = self.SKILLS_CONFIG.get(category)
        if not skills:
            logger.error("Category not found: %s", category)
            logger.info("Available categories: %s", ", ".join(sorted(self.SKILLS_CONFIG)))
            return

        for source_repo, source_path in skills:
            org, repo = source_repo.split("/", 1)
            skill_name = repo.replace("-sdk", "").replace("-", "_")
            self.import_skill(category, skill_name, org, source_repo, source_path)

        if print_summary:
            self._print_summary()

    def import_org(self, org: str) -> None:
        found = False
        for category, skills in self.SKILLS_CONFIG.items():
            for source_repo, source_path in skills:
                repo_org, repo = source_repo.split("/", 1)
                if repo_org.lower() == org.lower():
                    found = True
                    self.import_skill(category, repo.replace("-sdk", "").replace("-", "_"), repo_org, source_repo, source_path)
        if not found:
            logger.warning("No configured skills found for organization: %s", org)
        self._print_summary()

    def _print_summary(self) -> None:
        logger.info("Import complete: %s successful, %s failed", len(self.imported_skills), len(self.failed_skills))
        if not self.dry_run and self.imported_skills:
            metadata_file = SKILLS_DIR / "IMPORT_METADATA.json"
            metadata_file.write_text(
                json.dumps([asdict(skill) for skill in self.imported_skills], indent=2),
                encoding="utf-8",
            )
            logger.info("Metadata saved to %s", metadata_file)


def main() -> None:
    parser = argparse.ArgumentParser(description="Import ATLAS skill templates")
    parser.add_argument("--all", action="store_true", help="Import all configured skills")
    parser.add_argument("--category", help="Import one configured category")
    parser.add_argument("--org", help="Import all configured repositories for one organization")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing files")
    parser.add_argument("--github-token", help="GitHub token, or use GITHUB_TOKEN")
    args = parser.parse_args()

    importer = SkillsImporter(dry_run=args.dry_run, github_token=args.github_token)
    if args.category:
        importer.import_category(args.category)
    elif args.org:
        importer.import_org(args.org)
    else:
        importer.import_all()


if __name__ == "__main__":
    main()
