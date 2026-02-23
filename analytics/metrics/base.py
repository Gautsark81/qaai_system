from __future__ import annotations

import json
import logging
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, Mapping, Optional


logger = logging.getLogger("qaai_system.metrics")


@dataclass
class MetricContext:
    """
    Common context carried with every metric event.

    This is intentionally generic – strategy- and broker-specific fields
    can be added on top as needed.
    """

    env: str = "live"  # e.g. "live", "paper", "backtest"
    strategy_id: Optional[str] = None
    run_id: Optional[str] = None
    extra: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "env": self.env,
            "strategy_id": self.strategy_id,
            "run_id": self.run_id,
        }
        if self.extra:
            data["extra"] = self.extra
        return data


class MetricsSink:
    """
    Abstract sink for metrics.

    Implementations must be *best-effort* and never raise in normal usage.
    """

    def emit(self, name: str, payload: Mapping[str, Any]) -> None:
        raise NotImplementedError


class LoggingMetricsSink(MetricsSink):
    """
    Default sink that logs metrics as structured JSON via standard logging.

    This is:
    - dependency-free
    - easy to ship to ELK/Datadog/etc. using log shipping
    """

    def __init__(self, logger_name: str = "qaai_system.metrics"):
        self._logger = logging.getLogger(logger_name)

    def emit(self, name: str, payload: Mapping[str, Any]) -> None:
        record = {
            "ts": datetime.now(timezone.utc).isoformat(),
            "metric": name,
            "data": dict(payload),
        }
        try:
            self._logger.info(json.dumps(record, sort_keys=True))
        except Exception:  # noqa: BLE001
            # Fail-closed: never let metrics bring down the process
            logger.exception("Failed to emit metric", extra={"metric_name": name})


def monotonic_ns() -> int:
    """
    Wrapper around time.monotonic_ns() to allow easier testing/mocking.
    """
    return time.monotonic_ns()
