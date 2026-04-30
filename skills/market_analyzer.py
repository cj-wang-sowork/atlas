"""Free-data market analysis helper for ATLAS skills."""

from __future__ import annotations

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from pytrends.request import TrendReq

    PYTRENDS_AVAILABLE = True
except ImportError:
    TrendReq = None
    PYTRENDS_AVAILABLE = False


class MarketAnalyzer:
    """Analyzes market signals and records optional ATLAS learning events."""

    def __init__(self, market_router: Any = None, security_checker: Any = None, atlas_learner: Any = None) -> None:
        self.market_router = market_router
        self.security_checker = security_checker
        self.atlas_learner = atlas_learner
        self.logger = logging.getLogger(__name__)
        self.trends = TrendReq(hl="en-US", tz=360) if PYTRENDS_AVAILABLE and TrendReq else None
        self.analysis_cache: Dict[str, Dict[str, Any]] = {}

    def analyze_market(self, market_code: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
        if self.atlas_learner:
            self.atlas_learner.observe_access(market_code, "team", "market_analysis", True)

        market_info = self._get_market_info(market_code)
        keywords = keywords or self._default_keywords_for_market(market_code, market_info)
        analysis = {
            "market_code": market_code,
            "timestamp": datetime.utcnow().isoformat(),
            "data_sources": {
                "google_trends": False,
                "keywords_analyzed": len(keywords),
                "confidence": 0.0,
            },
            "trends": {},
            "recommendations": [],
        }

        if self.trends and keywords:
            try:
                analysis["trends"] = self._analyze_google_trends(keywords)
                analysis["data_sources"]["google_trends"] = True
                analysis["data_sources"]["confidence"] = 0.5
            except Exception as exc:  # pytrends raises provider-specific exceptions.
                self.logger.warning("Google Trends analysis failed: %s", exc)

        analysis["recommendations"] = self._generate_recommendations(analysis, market_info)
        self.analysis_cache[market_code] = analysis
        return analysis

    def _get_market_info(self, market_code: str) -> Optional[Dict[str, Any]]:
        if not self.market_router:
            return None
        if hasattr(self.market_router, "get_config"):
            config = self.market_router.get_config(market_code)
            return getattr(config, "__dict__", None) if config else None
        if hasattr(self.market_router, "get_market"):
            return self.market_router.get_market(market_code)
        return None

    def _analyze_google_trends(self, keywords: List[str]) -> Dict[str, Any]:
        if not self.trends:
            return {}
        selected = keywords[:5]
        self.trends.build_payload(kw_list=selected, cat=0, timeframe="today 3-m")
        interest_df = self.trends.interest_over_time()
        return {
            "keywords": selected,
            "timeframe": "last 3 months",
            "trend_direction": self._calculate_trend_direction(interest_df),
            "peak_dates": self._find_peak_dates(interest_df),
            "overall_trend": "rising" if self._is_trend_rising(interest_df) else "stable",
        }

    def _calculate_trend_direction(self, df: Any) -> str:
        if df.empty or len(df) < 2:
            return "unknown"
        first_val = df.iloc[0, 0]
        last_val = df.iloc[-1, 0]
        if last_val > first_val * 1.1:
            return "rising"
        if last_val < first_val * 0.9:
            return "falling"
        return "stable"

    def _find_peak_dates(self, df: Any) -> List[str]:
        if df.empty:
            return []
        top_peaks = df.nlargest(3, df.columns[0])
        return [str(date.date()) for date in top_peaks.index]

    def _is_trend_rising(self, df: Any) -> bool:
        if df.empty or len(df) < 2:
            return False
        return df.iloc[-1, 0] > df.iloc[0, 0]

    def _default_keywords_for_market(self, market_code: str, market_info: Optional[Dict[str, Any]] = None) -> List[str]:
        keywords_map = {
            "us-en": ["digital marketing", "social media", "ecommerce", "AI marketing"],
            "eu-de": ["digitales marketing", "social media", "datenschutz", "GDPR"],
            "ja-ja": ["digital marketing", "social media", "advertising"],
            "fr-fr": ["marketing digital", "reseaux sociaux", "commerce electronique"],
            "br-pt": ["marketing digital", "redes sociais", "ecommerce"],
        }
        if market_info and market_info.get("market_name"):
            return [str(market_info["market_name"]), "digital marketing", "AI marketing"]
        return keywords_map.get(market_code, ["digital marketing", "online marketing"])

    def _generate_recommendations(self, analysis: Dict[str, Any], market_info: Optional[Dict[str, Any]] = None) -> List[str]:
        recommendations = []
        if analysis["data_sources"]["google_trends"]:
            trend_direction = analysis["trends"].get("trend_direction", "unknown")
            if trend_direction == "rising":
                recommendations.append("Market interest is rising; consider increasing campaign tests.")
            elif trend_direction == "falling":
                recommendations.append("Market interest is falling; review messaging and channel mix.")
            else:
                recommendations.append("Market interest is stable; maintain current testing cadence.")
        else:
            recommendations.append("Install pytrends to add Google Trends data.")

        if market_info and market_info.get("region"):
            recommendations.append(f"Localize recommendations for the {market_info['region']} region.")
        recommendations.append("Collect more data points before making high-budget decisions.")
        return recommendations

    def get_cached_analysis(self, market_code: str) -> Optional[Dict[str, Any]]:
        return self.analysis_cache.get(market_code)

    def export_analysis(self, market_code: str, filepath: str) -> bool:
        analysis = self.get_cached_analysis(market_code)
        if not analysis:
            return False
        Path(filepath).write_text(json.dumps(analysis, indent=2), encoding="utf-8")
        return True


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    analyzer = MarketAnalyzer()
    print(json.dumps(analyzer.analyze_market("us-en"), indent=2))
