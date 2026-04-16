#!/usr/bin/env python3
"""
Five-Layer Learning System for OpenClaw Workspace
Manages enterprise, brand, department, team, and personal learning layers
with security controls, access verification, and multi-market support.
"""

import os
import re
import json
import hashlib
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum
from datetime import datetime


class LearningLevel(Enum):
      """Five-layer learning hierarchy"""
      ENTERPRISE = "enterprise"      # Public, organization-wide
    BRAND = "brand"                 # Internal, brand-specific
    DEPARTMENT = "department"       # Team-only, department-specific
    TEAM = "team"                   # Private, direct team
    PERSONAL = "personal"           # Local-only, never committed


class AccessLevel(Enum):
      """Access control markers"""
      PUBLIC = "@public"              # Enterprise level - public
    INTERNAL = "@internal"          # Brand/Department level - internal team
    TEAM_PRIVATE = "@team-private"  # Team level - direct team only
    PRIVATE = "@private"            # Personal level - private


@dataclass
class LearnFile:
      """Represents a single learning file"""
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
      """Validates learning files for security issues"""

    # Patterns that indicate credentials/sensitive data
      CREDENTIAL_PATTERNS = [
          r'(?i)(password|passwd|pwd)\s*[:=]\s*["\']?([^"\'\s]+)',
          r'(?i)(api[_-]?key|apikey)\s*[:=]\s*["\']?([^"\'\s]+)',
          r'(?i)(secret|token)\s*[:=]\s*["\']?([^"\'\s]+)',
          r'(?i)(private[_-]?key)\s*[:=]\s*["\']?([^"\'\s]+)',
          r'(?i)(auth|authorization)\s*[:=]\s*["\']?Bearer\s+([^"\'\s]+)',
          r'(?i)(ssh|rsa|dsa)[_-]?key\s*[:=]',
      ]

    PII_PATTERNS = [
              r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
              r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b',  # Phone
              r'(?i)(email|e-mail)\s*[:=]\s*[^@\s]+@[^\s]+',  # Email
    ]

    def __init__(self):
              self.logger = logging.getLogger(__name__)
              self.violations = []

    def validate_file(self, learn_file: LearnFile) -> Tuple[bool, List[str]]:
              """Validate a learning file for security violations"""
              self.violations = []

        # Check for credentials
              for pattern in self.CREDENTIAL_PATTERNS:
                            if re.search(pattern, learn_file.content):
                                              self.violations.append(
                                                                    f"⚠️ CREDENTIAL_LEAK: {learn_file.path} contains potential credential"
                                              )

                        # Check for PII
                        for pattern in self.PII_PATTERNS:
                                      if re.search(pattern, learn_file.content):
                                                        self.violations.append(
                                                                              f"⚠️ PII_LEAK: {learn_file.path} contains potential personally identifiable information"
                                                        )

                                  # Personal files must never be committed
                                  if learn_file.level == LearningLevel.PERSONAL:
                                                self.violations.append(
                                                                  f"🚫 PERSONAL_LAYER: {learn_file.path} should not be in git (add to .gitignore)"
                                                )

        return len(self.violations) == 0, self.violations


class LearnAccessControl:
      """Manages access control for learning layers"""

    # Access matrix: who can read what?
    ACCESS_MATRIX = {
              LearningLevel.ENTERPRISE: [LearningLevel.ENTERPRISE, LearningLevel.BRAND, 
                                                                            LearningLevel.DEPARTMENT, LearningLevel.TEAM],
              LearningLevel.BRAND: [LearningLevel.BRAND, LearningLevel.DEPARTMENT, 
                                                                 LearningLevel.TEAM],
              LearningLevel.DEPARTMENT: [LearningLevel.DEPARTMENT, LearningLevel.TEAM],
              LearningLevel.TEAM: [LearningLevel.TEAM],
              LearningLevel.PERSONAL: [],  # Never accessible from code
    }

    def __init__(self):
              self.logger = logging.getLogger(__name__)

    def can_access(self, user_level: LearningLevel, 
                                      resource_level: LearningLevel) -> bool:
                                                """Check if user at one level can access resource at another level"""
                                                accessible = self.ACCESS_MATRIX.get(user_level, [])
                                                return resource_level in accessible

    def get_accessible_files(self, user_level: LearningLevel,
                                                         files: List[LearnFile]) -> List[LearnFile]:
                                                                   """Filter files accessible to user's level"""
                                                                   return [f for f in files if self.can_access(user_level, f.level)]

    def verify_access_marker(self, learn_file: LearnFile) -> Tuple[bool, str]:
              """Verify file has correct access marker"""
        required_marker = self._get_required_marker(learn_file.level)

        if required_marker not in learn_file.content:
                      return False, f"Missing marker '{required_marker.value}' for {learn_file.level.value} level"

        return True, "Access marker verified"

    @staticmethod
    def _get_required_marker(level: LearningLevel) -> AccessLevel:
              """Get required access marker for learning level"""
        mapping = {
                      LearningLevel.ENTERPRISE: AccessLevel.PUBLIC,
                      LearningLevel.BRAND: AccessLevel.INTERNAL,
                      LearningLevel.DEPARTMENT: AccessLevel.INTERNAL,
                      LearningLevel.TEAM: AccessLevel.TEAM_PRIVATE,
                      LearningLevel.PERSONAL: AccessLevel.PRIVATE,
        }
        return mapping[level]


class MultiMarketLearnManager:
      """Manages learning across multiple markets"""

    def __init__(self, workspace_root: str = "~/.openclaw/workspace"):
              self.workspace_root = Path(workspace_root).expanduser()
        self.learn_root = self.workspace_root / "learn"
        self.logger = self._setup_logging()
        self.security_validator = LearnSecurityValidator()
        self.access_control = LearnAccessControl()

    def _setup_logging(self) -> logging.Logger:
              """Setup logging"""
        logger = logging.getLogger(__name__)
        logger.setLevel(logging.INFO)

        if not logger.handlers:
                      handler = logging.StreamHandler()
                      formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
                      handler.setFormatter(formatter)
                      logger.addHandler(handler)

        return logger

    def load_learn_files(self, level: Optional[LearningLevel] = None,
                                                market: Optional[str] = None,
                                                department: Optional[str] = None) -> List[LearnFile]:
                                                          """Load learning files with optional filtering"""
                                                          files = []

        if not self.learn_root.exists():
                      self.logger.warning(f"Learn root not found: {self.learn_root}")
                      return files

        # Determine directories to search
        if level:
                      search_dirs = [self.learn_root / level.value]
else:
            search_dirs = [d for d in self.learn_root.iterdir() 
                                                     if d.is_dir() and d.name in [l.value for l in LearningLevel]]

        for search_dir in search_dirs:
                      if not search_dir.exists():
                                        continue

                      for md_file in search_dir.rglob("*.md"):
                                        # Skip personal files in code
                                        if search_dir.name == "personal":
                                                              self.logger.warning(f"Skipping personal file (should not be in git): {md_file}")
                                                              continue

                                        # Parse and create LearnFile
                                        learn_file = self._parse_learn_file(md_file)

                # Filter by market if specified
                if market and learn_file.market and learn_file.market != market:
                                      continue

                # Filter by department if specified
                if department and learn_file.department and learn_file.department != department:
                                      continue

                files.append(learn_file)

        return files

    def _parse_learn_file(self, file_path: Path) -> LearnFile:
              """Parse a learning markdown file"""
        with open(file_path, 'r', encoding='utf-8') as f:
                      content = f.read()

        # Extract metadata from YAML front matter
        metadata = {}
        if content.startswith('---'):
                      parts = content.split('---', 2)
            if len(parts) >= 2:
                              for line in parts[1].split('\n'):
                                                    if ':' in line:
                                                                              key, value = line.split(':', 1)
                                                                              metadata[key.strip()] = value.strip().strip('"\'')

                                        # Determine learning level from file path
                                        level_str = file_path.parent.name
        try:
                      level = LearningLevel(level_str)
except ValueError:
            level = LearningLevel.ENTERPRISE

        # Determine access level
        access = self.access_control._get_required_marker(level)

        # Calculate checksum for audit
        checksum = hashlib.sha256(content.encode()).hexdigest()[:12]

        return LearnFile(
                      path=file_path,
                      level=level,
                      access=access,
                      content=content,
                      created=metadata.get('created', datetime.now().isoformat()),
                      author=metadata.get('author', 'unknown'),
                      market=metadata.get('market'),
                      department=metadata.get('department'),
                      checksum=checksum
        )

    def validate_all_files(self, level: Optional[LearningLevel] = None) -> Dict:
              """Validate all learning files for security issues"""
        files = self.load_learn_files(level)
        results = {
                      'total': len(files),
                      'valid': 0,
                      'violations': []
        }

        for learn_file in files:
                      is_valid, violations = self.security_validator.validate_file(learn_file)

            if is_valid:
                              results['valid'] += 1

            if violations:
                              results['violations'].extend(violations)

        return results

    def get_market_context(self, market: str, 
                                                    requesting_level: LearningLevel = LearningLevel.TEAM) -> Dict:
                                                              """Get all accessible learning for a specific market"""
                                                              files = self.load_learn_files(market=market)

        # Filter by access level
        accessible = self.access_control.get_accessible_files(requesting_level, files)

        context = {
                      'market': market,
                      'requesting_level': requesting_level.value,
                      'accessible_files': [
                                        {
                                                              'path': str(f.path),
                                                              'level': f.level.value,
                                                              'author': f.author,
                                                              'checksum': f.checksum,
                                        }
                                        for f in accessible
                      ]
        }

        return context

    def audit_security(self) -> Dict:
              """Comprehensive security audit"""
        audit_log = {
                      'timestamp': datetime.now().isoformat(),
                      'learn_files_found': 0,
                      'personal_files_detected': 0,
                      'security_violations': [],
                      'missing_access_markers': [],
                      'market_isolation_status': 'OK'
        }

        # Scan all files
        files = self.load_learn_files()
        audit_log['learn_files_found'] = len(files)

        # Check personal files (should not exist)
        personal_dir = self.learn_root / "personal"
        if personal_dir.exists():
                      personal_files = list(personal_dir.rglob("*.md"))
            if personal_files:
                              audit_log['personal_files_detected'] = len(personal_files)
                audit_log['security_violations'].append(
                                      f"⚠️ Found {len(personal_files)} personal files in git (should be .gitignored)"
                )

        # Validate all files
        validation = self.validate_all_files()
        audit_log['security_violations'].extend(validation['violations'])

        # Check access markers
        for learn_file in files:
                      is_valid, msg = self.access_control.verify_access_marker(learn_file)
            if not is_valid:
                              audit_log['missing_access_markers'].append(msg)

        return audit_log


def main():
      """CLI entry point"""
    import sys

    manager = MultiMarketLearnManager()

    if len(sys.argv) < 2:
              print("Usage: python learn_system.py [validate|audit|context|list]")
        return

    command = sys.argv[1]

    if command == "validate":
              results = manager.validate_all_files()
        print(json.dumps(results, indent=2))

elif command == "audit":
        audit = manager.audit_security()
        print(json.dumps(audit, indent=2))

elif command == "context":
        market = sys.argv[2] if len(sys.argv) > 2 else "default"
        context = manager.get_market_context(market)
        print(json.dumps(context, indent=2))

elif command == "list":
        files = manager.load_learn_files()
        for f in files:
                      print(f"{f.level.value:15} | {f.path.name:40} | {f.author:15} | {f.checksum}")


if __name__ == "__main__":
      main()
