#!/usr/bin/env python3
"""Five-layer learning files and access validation for ATLAS."""

from __future__ import annotations

import hashlib
import logging
import re
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class LearningLevel(Enum):
    ENTERPRISE = "enterprise"
    BRAND = "brand"
    DEPARTMENT = "department"
    TEAM = "team"
    PERSONAL = "personal"


class AccessLevel(Enum):
    PUBLIC = "@public"
    INTERNAL = "@internal"
    TEAM_PRIVATE = "@team-private"
    PRIVATE = "@private"


@dataclass
class LearnFile:
    path: Path
    level: LearningLevel
    access: AccessLevel
    content: str
    created: str
    author: str
    market: Optional[str] = None
    department: Optional[str] = None
    checksum: Optional[str] = None


class LearnSecurityValidator:
    """Detects obvious sensitive content in learning files."""

    CREDENTIAL_PATTERNS = [
        r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^'\"\s]+)",
        r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?([^'\"\s]+)",
        r"(?i)(secret|token)\s*[:=]\s*['\"]?([^'\"\s]+)",
        r"(?i)(private[_-]?key)\s*[:=]",
        r"(?i)(auth|authorization)\s*[:=]\s*['\"]?Bearer\s+([^'\"\s]+)",
    ]
    PII_PATTERNS = [
        r"\b\d{3}-\d{2}-\d{4}\b",
        r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
        r"(?i)(email|e-mail)\s*[:=]\s*[^@\s]+@[^\s]+",
    ]

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)
        self.violations: List[str] = []

    def validate_file(self, learn_file: LearnFile) -> Tuple[bool, List[str]]:
        self.violations = []

        for pattern in self.CREDENTIAL_PATTERNS:
            if re.search(pattern, learn_file.content):
                self.violations.append(f"CREDENTIAL_LEAK: {learn_file.path}")

        for pattern in self.PII_PATTERNS:
            if re.search(pattern, learn_file.content):
                self.violations.append(f"PII_LEAK: {learn_file.path}")

        if learn_file.level == LearningLevel.PERSONAL:
            self.violations.append(f"PERSONAL_LAYER_NOT_FOR_GIT: {learn_file.path}")

        return len(self.violations) == 0, list(self.violations)


class LearnAccessControl:
    """Access checks for the ATLAS five-layer hierarchy."""

    ACCESS_MATRIX = {
        LearningLevel.ENTERPRISE: {
            LearningLevel.ENTERPRISE,
            LearningLevel.BRAND,
            LearningLevel.DEPARTMENT,
            LearningLevel.TEAM,
        },
        LearningLevel.BRAND: {LearningLevel.BRAND, LearningLevel.DEPARTMENT, LearningLevel.TEAM},
        LearningLevel.DEPARTMENT: {LearningLevel.DEPARTMENT, LearningLevel.TEAM},
        LearningLevel.TEAM: {LearningLevel.TEAM},
        LearningLevel.PERSONAL: set(),
    }

    REQUIRED_MARKERS = {
        LearningLevel.ENTERPRISE: AccessLevel.PUBLIC,
        LearningLevel.BRAND: AccessLevel.INTERNAL,
        LearningLevel.DEPARTMENT: AccessLevel.INTERNAL,
        LearningLevel.TEAM: AccessLevel.TEAM_PRIVATE,
        LearningLevel.PERSONAL: AccessLevel.PRIVATE,
    }

    def __init__(self) -> None:
        self.logger = logging.getLogger(__name__)

    def can_access(self, user_level: LearningLevel, resource_level: LearningLevel) -> bool:
        if resource_level == LearningLevel.PERSONAL:
            return user_level == LearningLevel.PERSONAL
        return user_level in self.ACCESS_MATRIX.get(resource_level, set())

    def get_accessible_files(
        self, user_level: LearningLevel, learn_files: List[LearnFile]
    ) -> List[LearnFile]:
        return [item for item in learn_files if self.can_access(user_level, item.level)]

    def verify_access_marker(self, learn_file: LearnFile) -> Tuple[bool, str]:
        expected = self._get_required_marker(learn_file.level)
        if learn_file.access == expected:
            return True, "access marker is valid"
        return False, f"expected {expected.value}, got {learn_file.access.value}"

    @staticmethod
    def _get_required_marker(level: LearningLevel) -> AccessLevel:
        return LearnAccessControl.REQUIRED_MARKERS[level]


class MultiMarketLearnManager:
    """Loads and validates `learn/<level>/*.md` files."""

    def __init__(self, workspace_root: str = "~/.openclaw/workspace") -> None:
        self.workspace_root = Path(workspace_root).expanduser()
        self.learn_root = self.workspace_root / "learn"
        self.validator = LearnSecurityValidator()
        self.access_control = LearnAccessControl()
        self.logger = self._setup_logging()

    def _setup_logging(self) -> logging.Logger:
        logging.basicConfig(level=logging.INFO, format="%(levelname)s:%(name)s:%(message)s")
        return logging.getLogger(__name__)

    def load_learn_files(
        self, level: Optional[LearningLevel] = None, market: Optional[str] = None
    ) -> List[LearnFile]:
        levels = [level] if level else list(LearningLevel)
        files: List[LearnFile] = []
        for current_level in levels:
            for path in (self.learn_root / current_level.value).glob("**/*.md"):
                learn_file = self._parse_learn_file(path)
                if market and learn_file.market != market:
                    continue
                files.append(learn_file)
        return files

    def _parse_learn_file(self, file_path: Path) -> LearnFile:
        content = file_path.read_text(encoding="utf-8")
        metadata = self._parse_metadata(content)
        level_name = metadata.get("level", file_path.parent.name)
        access_name = metadata.get("access", AccessLevel.PRIVATE.value)
        return LearnFile(
            path=file_path,
            level=LearningLevel(level_name),
            access=AccessLevel(access_name),
            content=content,
            created=metadata.get("created", datetime.utcnow().date().isoformat()),
            author=metadata.get("author", "unknown"),
            market=metadata.get("market"),
            department=metadata.get("department"),
            checksum=hashlib.sha256(content.encode("utf-8")).hexdigest(),
        )

    def validate_all_files(self, level: Optional[LearningLevel] = None) -> Dict[str, object]:
        results = {"valid": True, "files": 0, "violations": []}
        for learn_file in self.load_learn_files(level=level):
            results["files"] += 1
            marker_ok, marker_message = self.access_control.verify_access_marker(learn_file)
            security_ok, violations = self.validator.validate_file(learn_file)
            if not marker_ok:
                violations.append(f"ACCESS_MARKER: {learn_file.path}: {marker_message}")
            if violations or not security_ok:
                results["valid"] = False
                results["violations"].extend(violations)
        return results

    def get_market_context(
        self, market: str, user_level: LearningLevel = LearningLevel.TEAM
    ) -> List[LearnFile]:
        files = self.load_learn_files(market=market)
        return self.access_control.get_accessible_files(user_level, files)

    def audit_security(self) -> Dict[str, object]:
        return self.validate_all_files()

    @staticmethod
    def _parse_metadata(content: str) -> Dict[str, str]:
        metadata: Dict[str, str] = {}
        if not content.startswith("---"):
            return metadata
        lines = content.splitlines()
        for line in lines[1:]:
            if line.strip() == "---":
                break
            if ":" in line:
                key, value = line.split(":", 1)
                metadata[key.strip()] = value.strip().strip("\"'")
        return metadata


def main() -> None:
    manager = MultiMarketLearnManager()
    print(manager.audit_security())


if __name__ == "__main__":
    main()
