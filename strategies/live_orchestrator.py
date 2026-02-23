# qaai_system/strategies/live_orchestrator.py
from __future__ import annotations

import logging
import os
import time
import json
from dataclasses import dataclass, field
from datetime import date
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger("qaai_system.LiveSignalEngine")
DAILY_PLAN_DIR = Path("configs/daily_run_plan")


def _env_bool(name: str, default: bool = False) -> bool:
    v = os.getenv(name)
    if v is None:
        return default
    return v.strip().lower() in {"1", "true", "yes", "on"}


def _env_str(name: str, default: str) -> str:
    v = os.getenv(name)
    return v if v is not None else default


def _env_int(name: str, default: int) -> int:
    v = os.getenv(name)
    if v is None:
        return default
    try:
        return int(v)
    except Exception:
        return default


@dataclass
class LiveSignalEngine:
    mode: str = "paper"
    strategy_id: str = field(default_factory=lambda: _env_str("QA_PRIMARY_STRATEGY_ID", "paper_test_strategy"))
    logger: logging.Logger = field(default_factory=lambda: logging.getLogger("qaai_system.LiveSignalEngine"))

    _cycle_index: int = field(default=0, init=False)
    _paper_trades_enabled: bool = field(default=False, init=False)
    _daily_plan: Optional[Dict[str, Any]] = field(default=None, init=False)

    def __post_init__(self) -> None:
        self._paper_trades_enabled = _env_bool("QA_PAPER_TEST_TRADES", False)
        self._load_daily_plan()
        self.logger.info(
            "LiveSignalEngine initialised",
            extra={
                "mode": self.mode,
                "strategy_id": self.strategy_id,
                "paper_test_trades_enabled": self._paper_trades_enabled,
            },
        )

    def _load_daily_plan(self) -> None:
        today = date.today().isoformat()
        path = DAILY_PLAN_DIR / f"{today}.json"
        if not path.exists():
            plans = sorted(DAILY_PLAN_DIR.glob("*.json"))
            if plans:
                path = plans[-1]
        if not path.exists():
            self._daily_plan = None
            self.logger.warning("No daily run plan found; will use QA_PAPER_TEST_TRADES fallback if enabled.")
            return
        try:
            with path.open("r", encoding="utf-8") as f:
                self._daily_plan = json.load(f)
            self.logger.info("Loaded daily run plan", extra={"path": str(path), "assignments": len(self._daily_plan.get("assignments", []))})
        except Exception:
            self._daily_plan = None
            self.logger.exception("Failed to load daily run plan; ignoring and continuing.")

    def generate_signals(self) -> List[Dict[str, Any]]:
        """
        Called each cycle by ExecutionEngine to get signals.

        Behavior:
         - If daily run plan exists -> generate simple market signals for assignments (paper-safe).
         - Else, if QA_PAPER_TEST_TRADES=1 and mode='paper', emit the single test order (alternate buy/sell).
        """
        self._cycle_index += 1
        signals: List[Dict[str, Any]] = []

        # 1) Try daily plan
        if self._daily_plan is not None:
            assignments = self._daily_plan.get("assignments", [])
            for a in assignments:
                symbol = a.get("symbol")
                sid = a.get("strategy_id")
                ver = str(a.get("version", "1"))
                pos_frac = float(a.get("capital_fraction", 0.0) or 0.0)
                # determine a safe, small qty for paper runs
                base_qty = int(_env_int("QA_PAPER_TEST_QTY", 1))
                # map capital_fraction to qty in a conservative way
                qty = max(1, int(base_qty * max(1.0, pos_frac * 100.0)))
                side = "BUY" if (self._cycle_index % 2 == 1) else "SELL"
                sig = {
                    "symbol": symbol,
                    "side": side,
                    "quantity": qty,
                    "price": 0.0,  # market
                    "position_size": qty,
                    "order_type": "MARKET",
                    "time_in_force": "DAY",
                    "strategy_id": sid,
                    "version": ver,
                    "tag": "daily_plan",
                    "timestamp": time.time(),
                }
                signals.append(sig)

            if signals:
                self.logger.debug("Generated signals from daily plan", extra={"count": len(signals)})
                return signals

        # 2) fallback to paper test single order
        if self.mode != "paper":
            return []

        if not self._paper_trades_enabled:
            return []

        now = time.time()
        symbol = _env_str("QA_PAPER_TEST_SYMBOL", "NSE:SBIN")
        qty = int(_env_int("QA_PAPER_TEST_QTY", 1))
        side = "BUY" if (self._cycle_index % 2 == 1) else "SELL"
        signal = {
            "symbol": symbol,
            "side": side,
            "quantity": qty,
            "price": 0.0,
            "position_size": qty,
            "order_type": "MARKET",
            "time_in_force": "DAY",
            "strategy_id": self.strategy_id,
            "version": "paper_test",
            "tag": "paper_test",
            "timestamp": now,
        }
        self.logger.info("generate_signals: emitting paper test order", extra={"signal": signal})
        return [signal]
