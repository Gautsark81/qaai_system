import pandas as pd
from qaai_system.signal_engine.signal_engine import SignalEngine


def test_signal_engine_run_and_generate():
    se = SignalEngine()
    df = se.run(["AAPL", "MSFT"])
    assert isinstance(df, pd.DataFrame)
    assert "symbol" in df.columns
    assert len(df) >= 1


def test_dynamic_sl_tp_and_sizeing():
    se = SignalEngine()
    df = pd.DataFrame({"price": [100, 200], "atr": [1.0, 2.0], "side": ["BUY", "SELL"]})
    out = se._dynamic_sl_tp(df, regime="bull")
    assert "sl_scaled" in out.columns
    assert "tp_scaled" in out.columns

    sized = se._size_by_drawdown(df, current_drawdown=0.1)
    assert "position_size" in sized.columns
    assert all(sized["position_size"] >= 1)


def test_blend_scores_and_explain_produces_reason():
    se = SignalEngine()
    df = pd.DataFrame(
        {"signal_strength": [0.8, 0.2], "ml_score": [0.7, 0.3], "price": [100, 200]}
    )
    out = se._blend_scores_and_explain(df)
    assert "blended_score" in out.columns
    assert "reason" in out.columns
    assert isinstance(out["reason"].iloc[0], str)


def test_register_trade_result_stores_feedback(tmp_path):
    se = SignalEngine()
    log_file = tmp_path / "feedback.csv"
    se._feedback_log = str(log_file)

    se.register_trade_result(
        trade_id="t1", pnl=-10.0, sl_hit=True, tp_hit=False, meta={"symbol": "AAPL"}
    )
    assert len(se._feedback_store) >= 1
    assert log_file.exists()
