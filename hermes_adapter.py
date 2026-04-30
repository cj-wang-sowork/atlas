"""Pattern-learning adapter for ATLAS."""

from __future__ import annotations

import hashlib
import json
import logging
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class LearningMode(Enum):
    OBSERVATION = "observation"
    ADAPTATION = "adaptation"
    OPTIMIZATION = "optimization"
    EMERGENCY = "emergency"


class PatternType(Enum):
    ACCESS_PATTERN = "access_pattern"
    VIOLATION_PATTERN = "violation_pattern"
    MARKET_BEHAVIOR = "market_behavior"
    SECURITY_RULE = "security_rule"
    PERFORMANCE_METRIC = "performance_metric"


@dataclass
class LearnedPattern:
    pattern_type: PatternType
    pattern_id: str
    market_code: str
    learning_level: str
    pattern_data: Dict[str, Any]
    confidence: float = 0.0
    occurrences: int = 0
    last_updated: datetime = field(default_factory=datetime.utcnow)
    source_data: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["pattern_type"] = self.pattern_type.value
        data["last_updated"] = self.last_updated.isoformat()
        return data


@dataclass
class AdaptationRule:
    rule_id: str
    rule_type: str
    market_code: str
    condition: Dict[str, Any]
    action: Dict[str, Any]
    auto_generated: bool = True
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


class HermesAdapter:
    """Observes repeated behavior and creates lightweight adaptive rules."""

    def __init__(
        self,
        market_router: Optional[Any] = None,
        learn_system: Optional[Any] = None,
        security_checker: Optional[Any] = None,
        logger: Optional[logging.Logger] = None,
    ) -> None:
        self.market_router = market_router
        self.learn_system = learn_system
        self.security_checker = security_checker
        self.logger = logger or logging.getLogger(__name__)
        self.learning_mode = LearningMode.OBSERVATION
        self.patterns: Dict[str, LearnedPattern] = {}
        self.adaptation_rules: Dict[str, AdaptationRule] = {}
        self.market_intelligence: Dict[str, Dict[str, Any]] = defaultdict(dict)
        self.learning_history: List[Dict[str, Any]] = []
        self.pattern_confidence_threshold = 0.7

    def observe_access(self, market_code: str, learning_level: str, action: str, success: bool = True) -> None:
        self._observe(
            PatternType.ACCESS_PATTERN,
            market_code,
            learning_level,
            {"action": action, "success": success},
        )

    def observe_violation(
        self, market_code: str, violation_type: str, learning_level: str, severity: str = "warning"
    ) -> None:
        self._observe(
            PatternType.VIOLATION_PATTERN,
            market_code,
            learning_level,
            {"violation_type": violation_type, "severity": severity},
        )

    def learn_market_behavior(self, market_code: str, behavior_data: Dict[str, Any]) -> None:
        self._observe(PatternType.MARKET_BEHAVIOR, market_code, "market", behavior_data)

    def get_adaptive_recommendations(self, market_code: str, context: Dict[str, Any]) -> List[Dict[str, Any]]:
        recommendations = []
        for rule in self.adaptation_rules.values():
            if rule.market_code != market_code:
                continue
            if all(context.get(key) == value for key, value in rule.condition.items()):
                recommendations.append(rule.to_dict())
        return recommendations

    def _observe(
        self, pattern_type: PatternType, market_code: str, learning_level: str, pattern_data: Dict[str, Any]
    ) -> None:
        key = json.dumps(
            {
                "type": pattern_type.value,
                "market": market_code,
                "level": learning_level,
                "data": pattern_data,
            },
            sort_keys=True,
        )
        pattern_id = self._generate_pattern_id(key)
        pattern = self.patterns.get(
            pattern_id,
            LearnedPattern(pattern_type, pattern_id, market_code, learning_level, pattern_data),
        )
        pattern.occurrences += 1
        pattern.last_updated = datetime.utcnow()
        pattern.confidence = min(1.0, pattern.occurrences / 10)
        pattern.source_data.append(pattern_type.value)
        self.patterns[pattern_id] = pattern
        self.learning_history.append(pattern.to_dict())

        if self.learning_mode in {LearningMode.ADAPTATION, LearningMode.OPTIMIZATION}:
            self._generate_adaptive_rule(pattern)

    def _generate_adaptive_rule(self, pattern: LearnedPattern) -> bool:
        if pattern.confidence < self.pattern_confidence_threshold:
            return False
        rule_id = self._generate_pattern_id(f"rule:{pattern.pattern_id}")
        self.adaptation_rules[rule_id] = AdaptationRule(
            rule_id=rule_id,
            rule_type=pattern.pattern_type.value,
            market_code=pattern.market_code,
            condition=pattern.pattern_data,
            action={"recommend": "reuse observed successful pattern"},
            confidence=pattern.confidence,
        )
        return True

    def _generate_pattern_id(self, pattern_key: str) -> str:
        return hashlib.sha256(pattern_key.encode("utf-8")).hexdigest()[:16]

    def set_learning_mode(self, mode: LearningMode) -> None:
        self.learning_mode = mode

    def export_patterns(self, output_path: str) -> bool:
        data = {
            "patterns": [pattern.to_dict() for pattern in self.patterns.values()],
            "rules": [rule.to_dict() for rule in self.adaptation_rules.values()],
        }
        Path(output_path).write_text(json.dumps(data, indent=2), encoding="utf-8")
        return True

    def import_patterns(self, input_path: str) -> bool:
        data = json.loads(Path(input_path).read_text(encoding="utf-8"))
        for item in data.get("patterns", []):
            item["pattern_type"] = PatternType(item["pattern_type"])
            item["last_updated"] = datetime.fromisoformat(item["last_updated"])
            pattern = LearnedPattern(**item)
            self.patterns[pattern.pattern_id] = pattern
        for item in data.get("rules", []):
            item["created_at"] = datetime.fromisoformat(item["created_at"])
            rule = AdaptationRule(**item)
            self.adaptation_rules[rule.rule_id] = rule
        return True

    def get_learning_summary(self) -> Dict[str, Any]:
        by_type = Counter(pattern.pattern_type.value for pattern in self.patterns.values())
        by_market = Counter(pattern.market_code for pattern in self.patterns.values())
        return {
            "mode": self.learning_mode.value,
            "patterns": len(self.patterns),
            "rules": len(self.adaptation_rules),
            "by_type": dict(by_type),
            "by_market": dict(by_market),
        }


if __name__ == "__main__":
    adapter = HermesAdapter()
    adapter.observe_access("us-en", "team", "campaign_read", True)
    print(adapter.get_learning_summary())
