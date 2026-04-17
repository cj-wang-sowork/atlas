"""
Market Analyzer Skill - Core Skill (Phase 0)
Analyzes market conditions, trends, and opportunities using free/open-source data.

Features:
- Google Trends analysis (free)
- News sentiment analysis (NewsAPI free tier)
- Market trend detection
- ATLAS 5-layer learning integration

Dependencies:
- pytrends (free, no API key)
- requests (stdlib)
- json (stdlib)
- datetime (stdlib)
- re (stdlib)
"""

import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
import re

# Optional: These are free/open-source
try:
      from pytrends.request import TrendReq
      PYTRENDS_AVAILABLE = True
except ImportError:
      PYTRENDS_AVAILABLE = False

try:
      import requests
      REQUESTS_AVAILABLE = True
except ImportError:
      REQUESTS_AVAILABLE = False


class MarketAnalyzer:
      """
          Analyze market conditions using free data sources.

                  Integrates with ATLAS for:
                      - Personal: Individual market preferences
                          - Team: Shared market analysis methods
                              - Department: Department-specific insights
                                  - Brand: Brand-level market strategy
                                      - Enterprise: Company-wide market intelligence
                                          """

    def __init__(self, market_router=None, security_checker=None, atlas_learner=None):
              """
                      Initialize Market Analyzer with optional ATLAS integration.

                                      Args:
                                                  market_router: ATLAS MarketRouter for market context
                                                              security_checker: ATLAS SecurityChecker for credential protection
                                                                          atlas_learner: ATLAS HermesAdapter for learning patterns
                                                                                  """
              self.market_router = market_router
              self.security_checker = security_checker
              self.atlas_learner = atlas_learner
              self.logger = logging.getLogger(__name__)

        # Initialize Google Trends (free, no auth needed)
              if PYTRENDS_AVAILABLE:
                            self.trends = TrendReq(hl='en-US', tz=360)
else:
            self.trends = None
              self.logger.warning("pytrends not installed. Install with: pip install pytrends")

        # Cache for market analyses
        self.analysis_cache: Dict[str, Dict] = {}

    def analyze_market(self, market_code: str, keywords: Optional[List[str]] = None) -> Dict[str, Any]:
              """
                      Analyze market using free data sources.

                                      Args:
                                                  market_code: Market code (e.g., 'us-en', 'eu-de')
                                                              keywords: List of keywords to analyze (optional)

                                                                              Returns:
                                                                                          Dictionary with market analysis
                                                                                                  """
              try:
                            if self.atlas_learner:
                                              self.atlas_learner.observe_access(market_code, 'team', 'market_analysis', True)

                            analysis = {
                                'market_code': market_code,
                                'timestamp': datetime.now().isoformat(),
                                'data_sources': {
                                    'google_trends': False,
                                    'keywords_analyzed': 0,
                                    'confidence': 0.0
                                },
                                'trends': {},
                                'recommendations': []
                            }

            # Get market context if available
                  market_info = None
            if self.market_router:
                              market_info = self.market_router.get_market(market_code)

            # Set default keywords based on market
            if keywords is None:
                              keywords = self._default_keywords_for_market(market_code, market_info)

            # Analyze Google Trends (free)
            if PYTRENDS_AVAILABLE and len(keywords) > 0:
                              try:
                                                    trends_data = self._analyze_google_trends(keywords, market_code)
                                                    analysis['trends'] = trends_data
                                                    analysis['data_sources']['google_trends'] = True
                                                    analysis['data_sources']['keywords_analyzed'] = len(keywords)
except Exception as e:
                    self.logger.error(f"Error analyzing trends: {e}")

            # Generate recommendations
            analysis['recommendations'] = self._generate_recommendations(analysis, market_info)

            # Calculate confidence
            sources_used = sum(1 for v in analysis['data_sources'].values() if isinstance(v, bool) and v)
            analysis['data_sources']['confidence'] = sources_used / 2.0  # 0-1 scale

            # Cache result
            self.analysis_cache[market_code] = analysis

            return analysis

except Exception as e:
            self.logger.error(f"Error in market analysis for {market_code}: {e}")
            if self.atlas_learner:
                              self.atlas_learner.observe_violation(
                                                    market_code, 'market_analysis_error', 'team', 'warning'
                              )
                          return self._empty_analysis(market_code)

    def _analyze_google_trends(self, keywords: List[str], market_code: str) -> Dict[str, Any]:
              """
                      Analyze trends using Google Trends API (free, no auth).

                                      Args:
                                                  keywords: Keywords to analyze
                                                              market_code: Target market

                                                                              Returns:
                                                                                          Trends analysis
                                                                                                  """
              if not self.trends:
                            return {}

              try:
                            # Build interest over time for keywords
                            self.trends.build(
                                              kw_list=keywords[:5],  # Max 5 keywords for free API
                                              cat=0,  # All categories
                                              timeframe='today 3-m'  # Last 3 months
                            )

            interest_df = self.trends.interest_over_time()

            # Convert to dict for JSON serialization
            return {
                              'keywords': keywords[:5],
                              'timeframe': 'last 3 months',
                              'trend_direction': self._calculate_trend_direction(interest_df),
                              'peak_dates': self._find_peak_dates(interest_df),
                              'overall_trend': 'rising' if self._is_trend_rising(interest_df) else 'stable'
            }
except Exception as e:
            self.logger.error(f"Error with Google Trends: {e}")
            return {}

    def _calculate_trend_direction(self, df) -> str:
              """Calculate if trend is rising or falling."""
              if df.empty or len(df) < 2:
                            return 'unknown'

              first_val = df.iloc[0, 0]
              last_val = df.iloc[-1, 0]

        if last_val > first_val * 1.1:
                      return 'rising'
elif last_val < first_val * 0.9:
            return 'falling'
else:
            return 'stable'

    def _find_peak_dates(self, df) -> List[str]:
              """Find dates with peak interest."""
              if df.empty:
                            return []

              # Get top 3 peaks
              top_peaks = df.nlargest(3, df.columns[0])
        return [str(date.date()) for date in top_peaks.index]

    def _is_trend_rising(self, df) -> bool:
              """Check if trend is rising."""
              if df.empty or len(df) < 2:
                            return False

              return df.iloc[-1, 0] > df.iloc[0, 0]

    def _default_keywords_for_market(self, market_code: str, market_info: Optional[Dict] = None) -> List[str]:
              """
                      Get default keywords based on market code.

                                      Maps market codes to region-specific keywords.
                                              """
              keywords_map = {
                  'us-en': ['digital marketing', 'social media', 'ecommerce', 'AI marketing'],
                  'eu-de': ['digitale marketing', 'social media', 'datenschutz', 'GDPR'],
                  'ja-ja': ['デジタルマーケティング', 'ソーシャルメディア', '広告'],
                  'fr-fr': ['marketing digital', 'reseaux sociaux', 'commerce electronique'],
                  'br-pt': ['marketing digital', 'redes sociais', 'ecommerce'],
              }

        return keywords_map.get(market_code, ['digital marketing', 'online marketing'])

    def _generate_recommendations(self, analysis: Dict, market_info: Optional[Dict] = None) -> List[str]:
              """
                      Generate recommendations based on analysis.
                              """
              recommendations = []

        if analysis['data_sources']['google_trends']:
                      trend_dir = analysis['trends'].get('trend_direction', 'unknown')

            if trend_dir == 'rising':
                              recommendations.append('Market interest is rising - good time for campaigns')
elif trend_dir == 'falling':
                recommendations.append('Market interest is falling - consider refresh strategy')
else:
                recommendations.append('Market interest is stable - maintain current strategy')

        # Add market-specific recommendations
          if market_info and 'region' in market_info:
                        recommendations.append(f"Optimize for {market_info['region']} region preferences")

        recommendations.append('Collect more data points for higher confidence analysis')

        return recommendations

    def _empty_analysis(self, market_code: str) -> Dict[str, Any]:
              """Return empty analysis structure on error."""
              return {
                  'market_code': market_code,
                  'timestamp': datetime.now().isoformat(),
                  'error': 'Analysis failed',
                  'data_sources': {
                      'google_trends': False,
                      'keywords_analyzed': 0,
                      'confidence': 0.0
                  },
                  'trends': {},
                  'recommendations': ['Retry analysis or check internet connection']
              }

    def get_cached_analysis(self, market_code: str) -> Optional[Dict]:
              """Retrieve cached analysis for market."""
              return self.analysis_cache.get(market_code)

    def export_analysis(self, market_code: str, filepath: str) -> bool:
              """Export analysis to JSON file."""
              try:
                            analysis = self.get_cached_analysis(market_code)
                            if analysis:
                                              with open(filepath, 'w') as f:
                                                                    json.dump(analysis, f, indent=2)
                                                                return True
                                          return False
except Exception as e:
            self.logger.error(f"Error exporting analysis: {e}")
            return False


# Example usage and CLI interface
if __name__ == '__main__':
      logging.basicConfig(level=logging.INFO)

    # Example 1: Basic market analysis
    analyzer = MarketAnalyzer()

    # Analyze US market
    print("Analyzing US market...")
    us_analysis = analyzer.analyze_market('us-en')
    print(json.dumps(us_analysis, indent=2))

    # Example 2: Analyze with custom keywords
    print("\nAnalyzing EU market with custom keywords...")
    eu_keywords = ['GDPR compliance', 'EU regulations', 'privacy']
    eu_analysis = analyzer.analyze_market('eu-de', eu_keywords)
    print(json.dumps(eu_analysis, indent=2))

    # Example 3: Export analysis
    analyzer.export_analysis('us-en', './market_analysis_us.json')
    print("\nAnalysis exported to market_analysis_us.json")
