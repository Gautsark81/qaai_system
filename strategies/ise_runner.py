# File: strategies/ise_runner.py
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Optional

from infra.logging import get_logger
from qaai_system.context.live_context import LiveContext
from qaai_system.execution.orchestrator import ExecutionOrchestrator
from screening.results import ScreeningResult
from strategies.ise_probability import (
    ISEProbabilityStrategy,
    StrategySignal,
)

logger = get_logger("strategies.ise_runner")


@dataclass
class ISERunnerConfig:
    """
    Execution-level config for ISE runner (not model features).

    This controls:
      - min/max quantity per signal
      - minimum price floor for orders
      - default ATR multipliers for SL / TP
      - trailing stop behaviour
    """
    min_qty: int = 1
    max_qty: int = 999999
    min_price: float = 0.05  # avoid obviously-bad zero prices

    # Default SL/TP ATR multipliers when signal.meta does not provide hints
    base_sl_atr_mult: float = 1.5
    base_tp_atr_mult: float = 3.0

    # Trailing behaviour
    # mode:
    #   - "none": no trailing
    #   - "breakeven": move to entry after some R
    #   - "atr_step": slide behind price by N*ATR after some R
    trail_mode: str = "atr_step"
    trail_start_after_R: float = 1.0
    trail_atr_mult: float = 1.5


class ISERunner:
    """
    Glue between ISEProbabilityStrategy and ExecutionOrchestrator.

    Responsibilities:
      - Pull StrategySignals from ISE (probability engine)
      - Convert them into order dicts compatible with orchestrator.submit_order()
      - Attach rich ISE meta (win_prob, regime, features, SL/TP/trailing, Kelly) into order["meta"]
      - Let orchestrator/router/risk handle reservations, caps, and circuit breakers
    """

    def __init__(
        self,
        ctx: LiveContext,
        ise_strategy: ISEProbabilityStrategy,
        orchestrator: ExecutionOrchestrator,
        config: Optional[ISERunnerConfig] = None,
    ) -> None:
        self.ctx = ctx
        self.strategy = ise_strategy
        self.orchestrator = orchestrator
        self.config = config or ISERunnerConfig()

    # ------------------------------------------------------------------
    # Core entrypoint
    # ------------------------------------------------------------------
    def run_once(
        self,
        screening_results: Dict[str, List[ScreeningResult]],
    ) -> List[Dict[str, Any]]:
        """
        Run ISE once over a screening snapshot and submit orders.

        Parameters
        ----------
        screening_results:
            Dict[screener_name, List[ScreeningResult]]

        Returns
        -------
        List[Dict[str, Any]]:
            List of orchestrator.submit_order responses (or error dicts).
        """
        # 1) Generate probabilistic signals from ISE
        try:
            signals: List[StrategySignal] = self.strategy.generate_signals(
                self.ctx, screening_results
            )
        except Exception as e:
            logger.exception("ISE generate_signals failed", exc_info=True)
            return [{"status": "error", "reason": f"ISE_ERROR: {e}"}]

        if not signals:
            return []

        responses: List[Dict[str, Any]] = []

        # 2) Convert each signal → order and submit through orchestrator
        for sig in signals:
            order = self._signal_to_order(sig)

            if order is None:
                # malformed / zero-sized – skip
                continue

            try:
                resp = self.orchestrator.submit_order(order)
            except Exception as e:
                logger.exception(
                    "orchestrator.submit_order failed for %s", sig.symbol, exc_info=True
                )
                resp = {
                    "status": "error",
                    "reason": str(e),
                    "symbol": sig.symbol,
                    "side": sig.side,
                }

            responses.append(resp)

        return responses

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------
    def _signal_to_order(self, sig: StrategySignal) -> Optional[Dict[str, Any]]:
        """
        Convert a StrategySignal into an executable order dict.

        The orchestrator + router will:
          - apply kill switches & circuit breakers
          - enforce symbol caps via RiskManager.check_symbol_cap()
          - persist reservations into provider._orders via patched_submit_order
        """
        cfg = self.config

        # --- qty ---
        try:
            raw_qty = max(float(sig.size), 0.0)
        except Exception:
            raw_qty = 0.0

        qty = int(round(raw_qty))
        qty = max(cfg.min_qty, qty)
        qty = min(cfg.max_qty, qty)

        if qty <= 0:
            logger.debug(
                "Dropping zero-sized ISE signal: %s %s size=%s",
                sig.symbol,
                sig.side,
                sig.size,
            )
            return None

        # --- price hint (used for risk notional, router, etc.) ---
        tf = getattr(self.strategy, "ise_config", None)
        tf_name = getattr(tf, "timeframe", None) if tf is not None else None
        use_tf = tf_name or getattr(self.ctx, "default_timeframe", "1m")
        price = float(self.ctx.get_last_price(sig.symbol, use_tf))
        if price <= 0:
            # final safeguard: avoid obviously invalid prices
            price = cfg.min_price

        # --- base meta from signal ---
        meta = dict(sig.meta or {})

        win_prob = float(meta.get("win_prob", meta.get("ise_win_prob", 0.0)))
        atr = float(meta.get("atr", meta.get("atr_lookback", 1.0) or 1.0))

        # --- Kelly fraction (hint from strategy config, not enforced here) ---
        kelly_frac = 0.0
        if tf is not None and hasattr(tf, "kelly_fraction"):
            try:
                kelly_frac = float(tf.kelly_fraction)
            except Exception:
                kelly_frac = 0.0

        # ------------------------------------------------------------------
        # SL / TP / Trailing logic
        # ------------------------------------------------------------------
        # Prefer hints from signal.meta if present (e.g. from ISE80pStrategy)
        sl_price = meta.get("sl_price_hint")
        tp_price = meta.get("tp_price_hint")
        sl_mult = meta.get("sl_atr_mult")
        tp_mult = meta.get("tp_atr_mult")

        if sl_price is None or tp_price is None:
            # Compute from win_prob + ATR + Kelly

            # normalise win_prob into [0.5, 0.99]
            p = max(0.5, min(win_prob or 0.5, 0.99))

            # map probability into risk_score 0..1
            risk_score = (p - 0.5) / 0.49  # 0..~1

            base_sl_mult = cfg.base_sl_atr_mult
            base_tp_mult = cfg.base_tp_atr_mult

            # let high probability + Kelly gently tighten SL & widen TP
            # risk_factor ranges roughly 0..1
            risk_factor = min(1.0, max(0.0, risk_score + kelly_frac))

            sl_mult = base_sl_mult * (1.0 - 0.3 * risk_factor)    # 30% tighter at high-conviction
            tp_mult = base_tp_mult * (1.0 + 0.3 * risk_factor)    # 30% further at high-conviction

            # compute distances in points
            sl_dist = sl_mult * atr
            tp_dist = tp_mult * atr

            if sig.side.upper() == "BUY":
                sl_price = price - sl_dist
                tp_price = price + tp_dist
            else:
                sl_price = price + sl_dist
                tp_price = price - tp_dist

        # R-multiple (TP vs SL distance)
        try:
            r_den = abs(price - float(sl_price))
            r_num = abs(float(tp_price) - price)
            r_multiple = r_num / r_den if r_den > 0 else 0.0
        except Exception:
            r_multiple = 0.0

        # trailing behaviour
        trail_mode = cfg.trail_mode
        trail_params: Dict[str, Any] = {
            "start_after_R": cfg.trail_start_after_R,
        }

        if trail_mode == "atr_step":
            trail_params["atr_mult"] = cfg.trail_atr_mult
        elif trail_mode == "breakeven":
            trail_params["move_to"] = "entry"

        # Put everything into meta (existing keys preserved if present)
        meta.setdefault("win_prob", win_prob)
        meta.setdefault("atr", atr)
        meta.setdefault("kelly_fraction", kelly_frac)

        meta.setdefault("ise_entry_price", price)
        meta.setdefault("ise_sl_price", float(sl_price))
        meta.setdefault("ise_tp_price", float(tp_price))
        meta.setdefault("ise_sl_atr_mult", float(sl_mult) if sl_mult is not None else cfg.base_sl_atr_mult)
        meta.setdefault("ise_tp_atr_mult", float(tp_mult) if tp_mult is not None else cfg.base_tp_atr_mult)
        meta.setdefault("ise_r_multiple", float(r_multiple))

        meta.setdefault("ise_trail_mode", trail_mode)
        meta.setdefault("ise_trail_params", trail_params)

        meta.update(
            {
                "strategy": sig.strategy,
                "ise_win_prob": win_prob,
                "ise_mode": "80p+",
                "ise_engine": "ISEProbabilityEngine",
            }
        )

        # --- build order dict for ExecutionOrchestrator.submit_order ---
        order: Dict[str, Any] = {
            "symbol": sig.symbol,
            "side": sig.side,           # "BUY" / "SELL"
            "qty": qty,
            "quantity": qty,            # orchestrator normalises this
            "price": price,
            "order_type": "MARKET",     # orchestrator/router can still route as needed
            "strategy_id": sig.strategy,
            "meta": meta,
        }

        logger.debug("ISE order built: %s", order)
        return order
