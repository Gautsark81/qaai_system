# tests/test_run_live_flow.py
"""
End-to-end smoke test for apps/run_live_dhan.py.
This test runs the run_once() flow with synthetic bars and checks the output shape.
"""
import importlib.util
import sys
from pathlib import Path
import pandas as pd
import pytest

# import the app module directly
spec = importlib.util.spec_from_file_location("run_live_dhan", str(Path("apps/run_live_dhan.py").resolve()))
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)

def make_bars():
    return mod.build_demo_bars(symbol="FOO", n=60, start_price=100.0)

def test_run_once_paper_mode_no_model(tmp_path):
    bars = make_bars()
    # pass a non-existent model path -> app should run with dummy model
    summary = mod.run_once(bars, model_path=None, paper=True, top_n=3)
    assert isinstance(summary, dict)
    assert "n_signals" in summary
    assert "orders" in summary
    # orders is a list (may be empty if no signals), but the app should always include it
    assert isinstance(summary["orders"], list)

def test_run_once_with_fake_model(tmp_path):
    # create a very small mock model pickle that the ModelAdapter in strategy_engine can accept
    fake_model_path = tmp_path / "fake_model.pkl"
    # create a simple dict that matches load_meta_model outputs used in run_live_dhan
    import pickle
    with open(fake_model_path, "wb") as fh:
        pickle.dump({"model": None}, fh)
    bars = make_bars()
    summary = mod.run_once(bars, model_path=str(fake_model_path), paper=True, top_n=2)
    assert isinstance(summary, dict)
    assert "orders" in summary
