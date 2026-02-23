# File: tests/strategies/test_ise_runner.py
from dataclasses import dataclass
from typing import Any, Dict, List

from qaai_system.context.live_context import LiveContext
from qaai_system.data.ohlcv_store import OHLCVStore
from qaai_system.data.feature_store import FeatureStore
from strategies.ise_runner import ISERunner, ISERunnerConfig
from strategies.ise_probability import StrategySignal


@dataclass
class FakeScreeningResult:
    symbol: str
    score: float


class FakeISEConfig:
    def __init__(self, timeframe: str = "1m", kelly_fraction: float = 0.0) -> None:
        self.timeframe = timeframe
        self.kelly_fraction = kelly_fraction


class FakeISEStrategy:
    """
    Minimal stand-in for ISEProbabilityStrategy:
      - has .ise_config
      - generate_signals() returns a hard-coded signal list
    """

    def __init__(self) -> None:
        self.ise_config = FakeISEConfig(timeframe="1m", kelly_fraction=0.1)

    def generate_signals(
        self,
        ctx: LiveContext,
        screening_results: Dict[str, List[FakeScreeningResult]],
    ) -> List[StrategySignal]:
        # Use ctx just to ensure we don't explode
        _ = ctx.get_last_price("NIFTY", "1m")

        meta = {
            "win_prob": 0.85,
            "atr": 10.0,
        }
        return [
            StrategySignal(
                strategy="ISE_TEST",
                symbol="NIFTY",
                side="BUY",
                size=2.3,
                meta=meta,
            )
        ]


class FakeOrchestrator:
    def __init__(self) -> None:
        self.submitted: List[Dict[str, Any]] = []

    def submit_order(self, order: Dict[str, Any]) -> Dict[str, Any]:
        self.submitted.append(order)
        return {"status": "accepted", "order": order}


def test_ise_runner_builds_order_with_sl_tp_and_trail():
    ohlcv = OHLCVStore()
    features = FeatureStore()
    ctx = LiveContext(
        ohlcv_store=ohlcv,
        feature_store=features,
        watchlists={"DAY_SCALP": ["NIFTY"]},
    )

    # seed some price so get_last_price works
    import datetime as dt
    from infra.time_utils import IST

    base = dt.datetime(2025, 1, 1, 9, 15, 0, tzinfo=IST)
    ohlcv.add_tick("NIFTY", 100.0, 10, base)
    ohlcv.add_tick("NIFTY", 101.0, 5, base + dt.timedelta(seconds=5))

    ise = FakeISEStrategy()
    orch = FakeOrchestrator()
    runner = ISERunner(
        ctx=ctx,
        ise_strategy=ise,  # type: ignore[arg-type]
        orchestrator=orch,  # type: ignore[arg-type]
        config=ISERunnerConfig(min_qty=1, max_qty=10),
    )

    screening_results = {"FAKE": [FakeScreeningResult(symbol="NIFTY", score=1.0)]}
    responses = runner.run_once(screening_results)

    assert len(responses) == 1
    assert len(orch.submitted) == 1

    order = orch.submitted[0]
    meta = order["meta"]

    # qty rounded & capped
    assert order["quantity"] >= 1

    # win_prob & ATR propagated
    assert meta["win_prob"] == 0.85
    assert meta["atr"] == 10.0

    # SL / TP / trailing fields present
    assert "ise_entry_price" in meta
    assert "ise_sl_price" in meta
    assert "ise_tp_price" in meta
    assert "ise_sl_atr_mult" in meta
    assert "ise_tp_atr_mult" in meta
    assert "ise_r_multiple" in meta

    assert "ise_trail_mode" in meta
    assert "ise_trail_params" in meta
    assert meta["ise_trail_mode"] in ("atr_step", "breakeven", "none")
