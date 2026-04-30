"""Cross-market intelligence helpers for ATLAS."""

from __future__ import annotations

import json
import logging
import statistics
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Dict, List, Optional


class InsightType(Enum):
    THREAT = "threat"
    OPPORTUNITY = "opportunity"
    ANOMALY = "anomaly"
    BENCHMARK = "benchmark"
    HEALTH = "health"


@dataclass
class MarketInsight:
    insight_type: InsightType
    market_code: str
    title: str
    details: Dict[str, Any]
    severity: str = "info"
    confidence: float = 0.0
    created_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["insight_type"] = self.insight_type.value
        data["created_at"] = self.created_at.isoformat()
        return data


@dataclass
class MarketBenchmark:
    market_code: str
    metric: str
    value: float
    percentile: float = 0.0


class MarketIntelligence:
    """Aggregates market metrics and emits simple insights."""

    def __init__(self, logger: Optional[logging.Logger] = None) -> None:
        self.logger = logger or logging.getLogger(__name__)
        self.market_metrics: Dict[str, Dict[str, Any]] = {}
        self.insights: List[MarketInsight] = []

    def aggregate_market_metrics(self, market_data: Dict[str, Any]) -> None:
        for market_code, metrics in market_data.items():
            self.market_metrics.setdefault(market_code, {}).update(metrics)

    def detect_cross_market_threats(self, violation_data: Dict[str, List[Dict[str, Any]]]) -> List[MarketInsight]:
        insights = []
        for market_code, violations in violation_data.items():
            critical = [item for item in violations if item.get("severity") in {"high", "critical"}]
            if len(critical) >= 3:
                insights.append(
                    MarketInsight(
                        InsightType.THREAT,
                        market_code,
                        "Repeated high-severity violations",
                        {"count": len(critical)},
                        severity="critical",
                        confidence=0.8,
                    )
                )
        self.insights.extend(insights)
        return insights

    def identify_opportunities(self, performance_data: Dict[str, Dict[str, float]]) -> List[MarketInsight]:
        insights = []
        for market_code, metrics in performance_data.items():
            conversion = metrics.get("conversion_rate")
            if conversion is not None and conversion >= 0.1:
                insights.append(
                    MarketInsight(
                        InsightType.OPPORTUNITY,
                        market_code,
                        "High-performing market pattern",
                        metrics,
                        severity="info",
                        confidence=0.7,
                    )
                )
        self.insights.extend(insights)
        return insights

    def detect_anomalies(self, market_patterns: Dict[str, Dict[str, float]]) -> List[MarketInsight]:
        values = [(market, data.get("score", 0.0)) for market, data in market_patterns.items()]
        if len(values) < 3:
            return []
        scores = [score for _, score in values]
        mean = statistics.mean(scores)
        stdev = statistics.pstdev(scores) or 1.0
        insights = []
        for market_code, score in values:
            z_score = abs((score - mean) / stdev)
            if z_score >= 2:
                insights.append(
                    MarketInsight(
                        InsightType.ANOMALY,
                        market_code,
                        "Market score is an outlier",
                        {"score": score, "z_score": z_score},
                        severity="warning",
                        confidence=min(1.0, z_score / 3),
                    )
                )
        self.insights.extend(insights)
        return insights

    def analyze_learning_level_performance(self, level_data: Dict[str, Dict[str, float]]) -> Dict[str, Any]:
        return {
            level: {
                "average": statistics.mean(metrics.values()) if metrics else 0.0,
                "metrics": metrics,
            }
            for level, metrics in level_data.items()
        }

    def generate_system_health_report(self) -> Dict[str, Any]:
        return {
            "generated_at": datetime.utcnow().isoformat(),
            "markets": len(self.market_metrics),
            "insights": len(self.insights),
            "critical_insights": len([item for item in self.insights if item.severity == "critical"]),
        }

    def export_intelligence_report(self, output_path: str) -> bool:
        report = self.generate_system_health_report()
        report["insights"] = [insight.to_dict() for insight in self.insights]
        Path(output_path).write_text(json.dumps(report, indent=2), encoding="utf-8")
        return True


if __name__ == "__main__":
    intelligence = MarketIntelligence()
    print(intelligence.generate_system_health_report())
