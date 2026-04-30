"""Market registration, context, routing, and statistics for ATLAS."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import datetime
from enum import Enum
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional


class MarketStatus(Enum):
    ACTIVE = "active"
    INACTIVE = "inactive"
    TESTING = "testing"
    DEPRECATED = "deprecated"


@dataclass
class MarketConfig:
    market_code: str
    market_name: str
    region: str
    language: str = "en"
    status: MarketStatus = MarketStatus.ACTIVE
    timezone: str = "UTC"
    currency: str = "USD"
    metadata: Dict[str, Any] = field(default_factory=dict)

    def validate(self) -> bool:
        return all([self.market_code, self.market_name, self.region, self.language])


@dataclass
class MarketContext:
    market_code: str
    created_at: datetime = field(default_factory=datetime.utcnow)
    session_id: str = ""
    user_agent: str = ""
    user_preferences: Dict[str, Any] = field(default_factory=dict)
    request_metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data = asdict(self)
        data["created_at"] = self.created_at.isoformat()
        return data


class MarketRouter:
    """Routes work to registered markets without hardcoded market limits."""

    def __init__(self, config_path: Optional[str] = None, logger: Optional[logging.Logger] = None) -> None:
        self.config_path = Path(config_path) if config_path else None
        self.logger = logger or logging.getLogger(__name__)
        self.markets: Dict[str, MarketConfig] = {}
        self.contexts: Dict[str, MarketContext] = {}
        self.routes: Dict[str, Dict[str, Callable[..., Any]]] = {}
        self._load_markets()

    def _load_markets(self) -> None:
        if not self.config_path or not self.config_path.exists():
            return
        data = json.loads(self.config_path.read_text(encoding="utf-8"))
        for market_data in data.get("markets", []):
            if isinstance(market_data.get("status"), str):
                market_data["status"] = MarketStatus(market_data["status"])
            self.register_market(MarketConfig(**market_data))

    def register_market(self, config: MarketConfig) -> bool:
        if not config.validate():
            self.logger.error("Invalid market config: %s", config)
            return False
        self.markets[config.market_code] = config
        self.contexts.setdefault(config.market_code, MarketContext(config.market_code))
        self.routes.setdefault(config.market_code, {})
        return True

    def deregister_market(self, market_code: str) -> bool:
        if market_code not in self.markets:
            return False
        del self.markets[market_code]
        self.contexts.pop(market_code, None)
        self.routes.pop(market_code, None)
        return True

    def get_config(self, market_code: str) -> Optional[MarketConfig]:
        return self.markets.get(market_code)

    def get_context(self, market_code: str, create_if_missing: bool = True) -> Optional[MarketContext]:
        if market_code in self.contexts:
            return self.contexts[market_code]
        if not create_if_missing:
            return None
        self.contexts[market_code] = MarketContext(market_code)
        return self.contexts[market_code]

    def register_route(self, market_code: str, route_name: str, handler: Callable[..., Any]) -> bool:
        if market_code not in self.markets:
            return False
        self.routes.setdefault(market_code, {})[route_name] = handler
        return True

    def execute_route(self, market_code: str, route_name: str, *args: Any, **kwargs: Any) -> List[Any]:
        handler = self.routes.get(market_code, {}).get(route_name)
        if not handler:
            return []
        return [handler(*args, **kwargs)]

    def list_markets(self, status_filter: Optional[MarketStatus] = None) -> List[MarketConfig]:
        markets = list(self.markets.values())
        if status_filter:
            markets = [market for market in markets if market.status == status_filter]
        return markets

    def get_market_stats(self) -> Dict[str, Any]:
        by_status: Dict[str, int] = {}
        by_region: Dict[str, int] = {}
        for market in self.markets.values():
            by_status[market.status.value] = by_status.get(market.status.value, 0) + 1
            by_region[market.region] = by_region.get(market.region, 0) + 1
        return {"total": len(self.markets), "by_status": by_status, "by_region": by_region}

    def export_config(self, output_path: str) -> bool:
        markets = []
        for market in self.markets.values():
            data = asdict(market)
            data["status"] = market.status.value
            markets.append(data)
        Path(output_path).write_text(json.dumps({"markets": markets}, indent=2), encoding="utf-8")
        return True


if __name__ == "__main__":
    router = MarketRouter()
    router.register_market(MarketConfig("us-en", "United States English", "North America"))
    print(router.get_market_stats())
