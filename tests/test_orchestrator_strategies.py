"""
Integration test: strategies -> portfolio aggregation -> orchestrator submit -> simulate fills -> poll feedback.

This is intentionally conservative and defensive about provider behavior so it works with
the existing PaperExecutionProvider used in your repo's tests.
"""

from typing import List, Dict, Any

from qaai_system.execution.orchestrator import ExecutionOrchestrator
from qaai_system.strategies.examples import (
    IntradayMomentumStrategy,
    SwingReversalStrategy,
)


class DummyFeedbackCollector:
    def __init__(self):
        self.trades = []

    def on_trade_closed(self, symbol_or_trade, pnl=None, qty=0):
        # support both dict or (symbol,pnl,qty) signature used across codebase
        if isinstance(symbol_or_trade, dict):
            self.trades.append(symbol_or_trade)
        else:
            self.trades.append({"symbol": symbol_or_trade, "pnl": pnl, "qty": qty})


def test_multi_strategy_flow_and_feedback_roundtrip():
    orch = ExecutionOrchestrator()
    # set a feedback target collector
    collector = DummyFeedbackCollector()
    orch._feedback_target = collector

    acct = orch._get_equity_safe()

    # create two strategies for same symbol to force portfolio_manager aggregation/netting behavior
    s1 = IntradayMomentumStrategy(symbol="XYZ", max_alloc_pct=0.02)
    s2 = SwingReversalStrategy(symbol="XYZ", max_alloc_pct=0.05)

    # create deterministic snapshots
    snap_intraday = {
        "price": 100.0,
        "atr": 1.0,
        "signal": "buy",
        "intraday_tp_pct": 0.10,
        "intraday_sl_pct": 0.02,
    }
    snap_swing = {
        "price": 100.0,
        "atr": 2.0,
        "change_pct": -0.06,
        "swing_tp_pct": 0.08,
        "swing_sl_pct": 0.04,
    }

    plans: List[Dict[str, Any]] = []
    plans.extend(s1.generate_plan(snap_intraday, acct))
    plans.extend(s2.generate_plan(snap_swing, acct))

    assert len(plans) >= 1, "expected at least one plan from strategies"

    # aggregate via orchestrator (will use portfolio_manager if available)
    aggregated = orch.aggregate_orders(plans)
    assert isinstance(aggregated, list)

    # submit aggregated orders
    submitted_ids = []
    for p in aggregated:
        res = orch.submit_order(p)
        # orchestrator returns dict for immediate filled responses or dict describing submitted order
        if isinstance(res, dict):
            oid = res.get("order_id") or res.get("orderid") or res.get("id")
            if oid:
                submitted_ids.append(str(oid))
            # if the order is immediately filled, simulate that it should be picked up by poll
            if str(res.get("status", "")).lower() in {"filled", "filled"}:
                # some providers return immediate fill dicts; in that case synthesize feedback
                # ensure collector receives something by simulating provider._orders if possible below
                pass
        elif isinstance(res, str):
            submitted_ids.append(res)
        else:
            # fallback: try to read provider._orders keys later
            pass

    # Make sure provider has stored orders for those ids (paper provider)
    provider = orch.provider
    # If no submitted_ids discovered, try to pull from provider._orders keys that match the symbol
    if not submitted_ids:
        try:
            for k, v in getattr(provider, "_orders", {}).items():
                if v.get("symbol") == "XYZ":
                    submitted_ids.append(str(k))
        except Exception:
            pass

    assert (
        len(submitted_ids) > 0
    ), "no orders were submitted; check provider/router behavior"

    # simulate fills by marking provider._orders[*]['status'] = 'FILLED' and adding realized_pnl
    for oid in submitted_ids:
        try:
            if hasattr(provider, "_orders") and oid in provider._orders:
                provider._orders[oid]["status"] = "FILLED"
                provider._orders[oid]["realized_pnl"] = 10.0
                # ensure necessary fields exist
                provider._orders[oid].setdefault("symbol", "XYZ")
                provider._orders[oid].setdefault(
                    "qty",
                    provider._orders[oid].get(
                        "qty", provider._orders[oid].get("quantity", 0)
                    ),
                )
                provider._orders[oid].setdefault(
                    "price", provider._orders[oid].get("price", 100.0)
                )
                provider._orders[oid].setdefault(
                    "side", provider._orders[oid].get("side", "sell")
                )
        except Exception:
            # best-effort: ignore if provider shape differs
            pass

    # call poll to dispatch feedback to collector
    orch.poll()

    # collector should have at least one trade or realized_pnl reported
    assert len(collector.trades) >= 1, "expected at least one feedback trade forwarded"

    # Also ensure strategies can accept feedback (simulate calling .on_feedback with a representative trade)
    trade_example = {"symbol": "XYZ", "pnl": 10.0, "qty": 1}
    s1.on_feedback(trade_example)
    s2.on_feedback(trade_example)
    assert s1.history and s2.history
