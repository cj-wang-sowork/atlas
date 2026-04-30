"""Security checks for ATLAS learning files and runtime content."""

from __future__ import annotations

import json
import logging
import re
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple


class ViolationSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class SecurityViolation:
    violation_type: str
    message: str
    severity: ViolationSeverity = ViolationSeverity.WARNING
    market_code: Optional[str] = None
    file_path: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, str]:
        data = asdict(self)
        data["severity"] = self.severity.value
        data["created_at"] = self.created_at.isoformat()
        return data


class SecurityChecker:
    """Detects common secret, PII, path, and access-marker issues."""

    CREDENTIAL_PATTERNS = {
        "api_key": r"(?i)(api[_-]?key|apikey)\s*[:=]\s*['\"]?[^'\"\s]+",
        "password": r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?[^'\"\s]+",
        "token": r"(?i)(secret|token)\s*[:=]\s*['\"]?[^'\"\s]+",
        "bearer": r"(?i)authorization\s*[:=]\s*['\"]?Bearer\s+[^'\"\s]+",
        "private_key": r"-----BEGIN [A-Z ]*PRIVATE KEY-----",
    }
    PII_PATTERNS = {
        "ssn": r"\b\d{3}-\d{2}-\d{4}\b",
        "phone": r"\b(?:\+?1[-.\s]?)?\(?[0-9]{3}\)?[-.\s]?[0-9]{3}[-.\s]?[0-9]{4}\b",
        "email": r"(?i)(email|e-mail)\s*[:=]\s*[^@\s]+@[^\s]+",
    }

    def __init__(self, audit_log_path: Optional[str] = None, logger: Optional[logging.Logger] = None) -> None:
        self.audit_log_path = Path(audit_log_path).expanduser() if audit_log_path else None
        self.logger = logger or logging.getLogger(__name__)
        self.violations: List[SecurityViolation] = []

    def scan_content(
        self, content: str, market_code: Optional[str] = None, file_path: Optional[str] = None
    ) -> Tuple[bool, List[SecurityViolation]]:
        found: List[SecurityViolation] = []
        for name, pattern in {**self.CREDENTIAL_PATTERNS, **self.PII_PATTERNS}.items():
            if re.search(pattern, content):
                severity = ViolationSeverity.CRITICAL if name in self.CREDENTIAL_PATTERNS else ViolationSeverity.HIGH
                found.append(SecurityViolation(name, f"Detected {name}", severity, market_code, file_path))
        for violation in found:
            self._record_violation(violation)
        return len(found) == 0, found

    def validate_content(
        self, content: str, market_code: Optional[str] = None, file_path: Optional[str] = None
    ) -> Tuple[bool, List[SecurityViolation]]:
        return self.scan_content(content, market_code, file_path)

    def validate_file_path(self, file_path: str) -> Tuple[bool, str]:
        path = Path(file_path)
        if ".." in path.parts:
            return False, "path traversal is not allowed"
        if self._is_version_control_path(file_path):
            return False, "version-control internals are not valid learning paths"
        return True, "path is valid"

    def validate_access_marker(self, content: str) -> Tuple[bool, str]:
        if self._has_valid_access_marker(content):
            return True, "access marker found"
        return False, "missing access marker: @public, @internal, @team-private, or @private"

    def _has_valid_access_marker(self, content: str) -> bool:
        return any(marker in content for marker in ["@public", "@internal", "@team-private", "@private"])

    def _is_version_control_path(self, file_path: str) -> bool:
        return ".git" in Path(file_path).parts

    def _record_violation(self, violation: SecurityViolation) -> None:
        self.violations.append(violation)
        if self.audit_log_path:
            self.audit_log_path.parent.mkdir(parents=True, exist_ok=True)
            with self.audit_log_path.open("a", encoding="utf-8") as handle:
                handle.write(json.dumps(violation.to_dict()) + "\n")

    def get_violations(
        self, market_code: Optional[str] = None, severity: Optional[ViolationSeverity] = None
    ) -> List[SecurityViolation]:
        results = self.violations
        if market_code:
            results = [item for item in results if item.market_code == market_code]
        if severity:
            results = [item for item in results if item.severity == severity]
        return results

    def clear_violations(self) -> int:
        count = len(self.violations)
        self.violations = []
        return count

    def export_audit_log(self, output_path: str) -> bool:
        data = [violation.to_dict() for violation in self.violations]
        Path(output_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True


if __name__ == "__main__":
    checker = SecurityChecker()
    print(checker.validate_content("hello"))
