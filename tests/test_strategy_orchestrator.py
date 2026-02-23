# tests/test_strategy_orchestrator.py
import pandas as pd
import pytest

from modules.strategy.orchestrator import StrategyOrchestrator

class FakeStrategy:
    def __init__(self, name="fake"):
        self.name = name
        self.prepared = False

    def prepare(self, hist):
        self.prepared = True

    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        # simple rule: BUY if close_z > 1.0 else 0
        out = pd.DataFrame()
        out["signal"] = df.get("close_z", pd.Series([0]*len(df))).apply(lambda v: 1 if v > 1.0 else 0)
        return out

class FakeMetaModel:
    def predict_proba(self, X):
        # accept numpy array, return list of dicts with p_buy/p_sell
        out = []
        for _ in range(X.shape[0]):
            out.append({"p_buy": 0.8, "p_sell": 0.1, "p_hold": 0.1})
        return out

class FakeRouter:
    def __init__(self):
        self.sent = []

    def send(self, order):
        self.sent.append(order)
        return {"ok": True, "order_id": "x123"}

def make_df(rows):
    return pd.DataFrame(rows)

def test_orchestrator_with_meta_and_router():
    # setup
    strat = FakeStrategy(name="rules")
    mm = FakeMetaModel()
    router = FakeRouter()
    cfg = {"feature_cols": ["close_z"], "model_thresholds": {"min_p_buy": 0.7}, "dry_run": False}
    orch = StrategyOrchestrator(strategies={"rules": strat}, meta_model=mm, order_router=router, cfg=cfg)

    hist = [{"close_z": 0.5}, {"close_z": 1.2}]
    orch.prepare(hist)

    # latest fused row batch with three rows
    df = make_df([
        {"symbol": "TCS", "close_z": 0.5, "price": 100},
        {"symbol": "TCS", "close_z": 1.2, "price": 101},
        {"symbol": "TCS", "close_z": 2.0, "price": 102},
    ])

    out = orch.run_once(df)
    # ensure probabilities were added
    assert "p_buy" in out.columns
    # aggregated_signal should be 0/1
    assert set(out["aggregated_signal"].unique()).issubset({0,1})
    # final_signal respects model threshold (min_p_buy 0.7 -> rows with p_buy 0.8 keep BUY)
    assert out.loc[1, "final_signal"] == 1
    # order(s) should have been sent for rows with final_signal==1
    sent = router.sent
    assert len(sent) >= 1
    assert sent[0]["symbol"] == "TCS"
