"""
  Hermes Self-Learning Adapter - AI Learning System Integration
  ==============================================================
  Integrates market_router, learn_system, and security_checker
  with Hermes' self-learning patterns for adaptive market behavior.

  Features:
- Pattern learning from market interactions
- Security rule adaptation based on violations
- Market intelligence sharing across learning levels
- Behavioral adaptation and optimization
- Self-correcting systems based on feedback

@access: @internal
  @version: 1.0
  @depends: market_router.py, learn_system.py, security_checker.py
  """

  import logging
import json
from typing import Dict, List, Optional, Any, Callable, Tuple
  from dataclasses import dataclass, field, asdict
  from enum import Enum
from datetime import datetime, timedelta
  from collections import defaultdict, Counter
  from pathlib import Path
import hashlib


class LearningMode(Enum):
    """System learning modes"""
      OBSERVATION = "observation"  # Passive learning
      ADAPTATION = "adaptation"    # Active learning & adjustment
      OPTIMIZATION = "optimization"  # Performance tuning
      EMERGENCY = "emergency"      # Safety mode


  class PatternType(Enum):
    """Types of patterns learned"""
      ACCESS_PATTERN = "access_pattern"
      VIOLATION_PATTERN = "violation_pattern"
      MARKET_BEHAVIOR = "market_behavior"
      SECURITY_RULE = "security_rule"
      PERFORMANCE_METRIC = "performance_metric"


  @dataclass
  class LearnedPattern:
    """A learned pattern from market behavior"""
          pattern_type: PatternType
    pattern_id: str
      market_code: str
      learning_level: str
      pattern_data: Dict[str, Any]
      confidence: float = 0.0  # 0-1 confidence score
    occurrences: int = 0
      last_updated: datetime = field(default_factory=datetime.utcnow)
      source_data: List[str] = field(default_factory=list)  # Sanitized examples

      def to_dict(self) -> Dict:
        """Convert to dictionary"""
          return {
              **asdict(self),
              "pattern_type": self.pattern_type.value,
              "last_updated": self.last_updated.isoformat()
  }


@dataclass
class AdaptationRule:
    """Auto-generated security or access rule from learning"""
      rule_id: str
    rule_type: str  # security_rule, access_rule, etc
      market_code: str
      condition: Dict[str, Any]
      action: Dict[str, Any]
      auto_generated: bool = True
      confidence: float = 0.0
      created_at: datetime = field(default_factory=datetime.utcnow)


  class HermesAdapter:
    """
          Self-learning system adapter for OpenClaw five-layer learning.

      Integrates market routing, learning system, and security with
    Hermes' pattern recognition and adaptive behavior.

      Architecture:
    - Observation Layer: Monitors all system interactions
    - Pattern Layer: Extracts and refines patterns
    - Adaptation Layer: Generates and applies rules
    - Intelligence Layer: Shares learning across markets/levels
      """

      def __init__(self, 
                 market_router: Optional[Any] = None,
                 learn_system: Optional[Any] = None,
                 security_checker: Optional[Any] = None,
                 logger: Optional[logging.Logger] = None):
        """
          Initialize Hermes adapter.

          Args:
            market_router: MarketRouter instance
            learn_system: MultiMarketLearnManager instance
            security_checker: SecurityChecker instance
            logger: Logger instance
        """
          self.market_router = market_router
          self.learn_system = learn_system
          self.security_checker = security_checker
          self.logger = logger or logging.getLogger(__name__)

          self.learning_mode = LearningMode.OBSERVATION
          self.patterns: Dict[str, LearnedPattern] = {}
        self.adaptation_rules: Dict[str, AdaptationRule] = {}
        self.market_intelligence: Dict[str, Dict] = defaultdict(dict)
        self.learning_history: List[Dict] = []
          self.pattern_confidence_threshold = 0.7

      def observe_access(self, market_code: str, learning_level: str, 
                      access_type: str, success: bool) -> None:
        """
          Observe an access event for learning.

        Args:
            market_code: Market code
            learning_level: Learning level accessed
            access_type: Type of access (read/write/exec)
            success: Whether access was successful
        """
          pattern_key = f"{market_code}:{learning_level}:{access_type}"

          if pattern_key not in self.patterns:
            self.patterns[pattern_key] = LearnedPattern(
                  pattern_type=PatternType.ACCESS_PATTERN,
                  pattern_id=self._generate_pattern_id(pattern_key),
                  market_code=market_code,
                  learning_level=learning_level,
                  pattern_data={"access_type": access_type, "successes": 0, "failures": 0}
              )

          pattern = self.patterns[pattern_key]
          pattern.occurrences += 1

          if success:
            pattern.pattern_data["successes"] = pattern.pattern_data.get("successes", 0) + 1
                      else:
            pattern.pattern_data["failures"] = pattern.pattern_data.get("failures", 0) + 1

          # Calculate confidence
          total = pattern.pattern_data.get("successes", 0) + pattern.pattern_data.get("failures", 0)
          if total > 0:
            pattern.confidence = pattern.pattern_data.get("successes", 0) / total

      def observe_violation(self, market_code: str, violation_type: str,
                         learning_level: str, severity: str) -> None:
        """
          Observe a security violation for learning.

        Args:
            market_code: Market code
            violation_type: Type of violation
            learning_level: Learning level where violation occurred
            severity: Severity level
        """
          pattern_key = f"{market_code}:{violation_type}"

          if pattern_key not in self.patterns:
            self.patterns[pattern_key] = LearnedPattern(
                              pattern_type=PatternType.VIOLATION_PATTERN,
                              pattern_id=self._generate_pattern_id(pattern_key),
                              market_code=market_code,
                              learning_level=learning_level,
                              pattern_data={"violation_type": violation_type, "severity": severity, "count": 0}
                          )

                      pattern = self.patterns[pattern_key]
          pattern.occurrences += 1
          pattern.pattern_data["count"] = pattern.occurrences

          # Adapt security rules if violation threshold exceeded
          if pattern.occurrences > 3 and self.learning_mode in [LearningMode.ADAPTATION, LearningMode.OPTIMIZATION]:
            self._generate_adaptive_rule(pattern)

      def learn_market_behavior(self, market_code: str, behavior_data: Dict[str, Any]) -> None:
        """
          Learn market-specific behaviors and patterns.

          Args:
            market_code: Market code
            behavior_data: Dictionary of observed behaviors
        """
          intelligence_key = f"{market_code}:behavior"

        if intelligence_key not in self.market_intelligence:
            self.market_intelligence[intelligence_key] = {
                  "behaviors": Counter(),
                  "last_updated": datetime.utcnow().isoformat()
  }

        for behavior, count in behavior_data.items():
            self.market_intelligence[intelligence_key]["behaviors"][behavior] += count
            self.market_intelligence[intelligence_key]["last_updated"] = datetime.utcnow().isoformat()

          self.logger.debug(f"Learned behaviors for market {market_code}: {dict(self.market_intelligence[intelligence_key]['behaviors'])}")

    def get_adaptive_recommendations(self, market_code: str, 
                                     context: Dict[str, Any]) -> List[Dict]:
        """
          Get AI-recommended adaptations based on learned patterns.

          Args:
            market_code: Market code
            context: Current context dictionary

        Returns:
            List of recommendations
        """
        recommendations = []

        # Find relevant patterns for this market
        market_patterns = {k: v for k, v in self.patterns.items() 
                                    if v.market_code == market_code and v.confidence >= self.pattern_confidence_threshold}

        for pattern_key, pattern in market_patterns.items():
            if pattern.pattern_type == PatternType.ACCESS_PATTERN:
                if pattern.confidence > 0.9:
                    recommendations.append({
                          "type": "access_optimization",
                          "pattern": pattern_key,
                          "recommendation": f"Optimize {pattern.pattern_data['access_type']} access for {pattern.learning_level}",
                          "confidence": pattern.confidence
  })
              elif pattern.pattern_type == PatternType.VIOLATION_PATTERN:
                if pattern.occurrences > 5:
                    recommendations.append({
                          "type": "security_hardening",
                          "pattern": pattern_key,
                          "recommendation": f"Strengthen security for {pattern.pattern_data['violation_type']}",
                          "confidence": pattern.confidence
  })

          return recommendations

      def _generate_adaptive_rule(self, pattern: LearnedPattern) -> bool:
        """
          Auto-generate adaptation rule from learned pattern.

          Args:
            pattern: Learned pattern

        Returns:
            True if rule created
        """
        rule_id = f"auto_{pattern.pattern_id}"

          if rule_id in self.adaptation_rules:
              return False

          rule = AdaptationRule(
            rule_id=rule_id,
            rule_type="security_rule",
            market_code=pattern.market_code,
            condition={"pattern_match": pattern.pattern_id},
              action={"block": True, "log": True},
              confidence=pattern.confidence
          )

          self.adaptation_rules[rule_id] = rule
          self.logger.info(f"Auto-generated rule: {rule_id} with confidence {rule.confidence}")
        return True

      def _generate_pattern_id(self, pattern_key: str) -> str:
        """Generate consistent pattern ID from key."""
          return hashlib.md5(pattern_key.encode()).hexdigest()[:8]

      def set_learning_mode(self, mode: LearningMode) -> None:
        """
          Change system learning mode.

          Args:
            mode: New learning mode
        """
          old_mode = self.learning_mode
          self.learning_mode = mode
          self.logger.info(f"Learning mode changed from {old_mode.value} to {mode.value}")

    def export_patterns(self, output_path: str) -> bool:
        """
          Export learned patterns to JSON file.

          Args:
            output_path: Output file path

        Returns:
            True if successful
        """
        try:
            data = {
                              "exported_at": datetime.utcnow().isoformat(),
                              "learning_mode": self.learning_mode.value,
                              "total_patterns": len(self.patterns),
                              "patterns": {k: v.to_dict() for k, v in self.patterns.items()},
                "adaptation_rules": {k: asdict(v) for k, v in self.adaptation_rules.items()},
                  "market_intelligence": {k: dict(v) if isinstance(v, dict) else v 
                                       for k, v in self.market_intelligence.items()}
                                         }

            with open(output_path, 'w', encoding='utf-8') as f:
                            json.dump(data, f, indent=2, default=str)

                                          self.logger.info(f"Exported {len(self.patterns)} patterns to {output_path}")
            return True
                      except Exception as e:
                        self.logger.error(f"Failed to export patterns: {e}")
            return False

                  def import_patterns(self, input_path: str) -> bool:
        """
                      Import learned patterns from JSON file.

                      Args:
            input_path: Input file path

        Returns:
                        True if successful
        """
        try:
                        with open(input_path, 'r', encoding='utf-8') as f:
                data = json.load(f)

                          # Import patterns
                          for pattern_id, pattern_dict in data.get("patterns", {}).items():
                pattern = LearnedPattern(
                                  pattern_type=PatternType[pattern_dict["pattern_type"]],
                                  pattern_id=pattern_dict["pattern_id"],
                                  market_code=pattern_dict["market_code"],
                                  learning_level=pattern_dict["learning_level"],
                                  pattern_data=pattern_dict["pattern_data"],
                                  confidence=pattern_dict["confidence"],
                                  occurrences=pattern_dict["occurrences"]
                              )
                              self.patterns[pattern_id] = pattern

                          self.logger.info(f"Imported {len(self.patterns)} patterns from {input_path}")
            return True
                      except Exception as e:
                        self.logger.error(f"Failed to import patterns: {e}")
            return False

                  def get_learning_summary(self) -> Dict[str, Any]:
        """Get summary of current learning state"""
                      return {
                          "learning_mode": self.learning_mode.value,
                          "total_patterns": len(self.patterns),
                          "adaptation_rules": len(self.adaptation_rules),
                          "pattern_types": {
                              pt.value: len([p for p in self.patterns.values() if p.pattern_type == pt])
                for pt in PatternType
                                },
                                            "average_confidence": sum(p.confidence for p in self.patterns.values()) / max(len(self.patterns), 1),
                                            "high_confidence_patterns": len([p for p in self.patterns.values() if p.confidence > 0.8])
                                }


# CLI Entry Point
if __name__ == "__main__":
    logging.basicConfig(
          level=logging.INFO,
          format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
      )

      # Example usage
      adapter = HermesAdapter()
      adapter.set_learning_mode(LearningMode.ADAPTATION)

      # Simulate learning
      adapter.observe_access("us-en", "personal", "read", True)
      adapter.observe_access("us-en", "personal", "read", True)
      adapter.observe_access("us-en", "personal", "write", False)
      adapter.observe_violation("us-en", "credential_leak", "personal", "critical")
      adapter.learn_market_behavior("us-en", {"high_traffic": 5, "normal_traffic": 2})

      # Get recommendations
      recommendations = adapter.get_adaptive_recommendations("us-en", {})
      print(f"\nAdaptive Recommendations:")
    for rec in recommendations:
        print(f"  - {rec['recommendation']} (confidence: {rec['confidence']:.1%})")

    # Summary
      summary = adapter.get_learning_summary()
      print(f"\nLearning Summary:")
    print(json.dumps(summary, indent=2))
  
