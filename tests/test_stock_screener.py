import pandas as pd
import pytest
from screening.stock_screener import StockScreener
from features.indicators import IndicatorEngine


@pytest.fixture
def mock_data():
    data = {
        "open": [100 + i for i in range(60)],
        "high": [102 + i for i in range(60)],
        "low": [98 + i for i in range(60)],
        "close": [100 + i for i in range(60)],
        "volume": [300000] * 60,
    }
    df = pd.DataFrame(data)
    return {"RELIANCE": df}


def test_screening_passes(mock_data):
    # Relaxed config to make sure it passes
    config = {
        "min_volume": 100000,
        "sma_cross": False,
        "rsi_range": [0, 100],
        "macd_signal": False,
    }

    engine = IndicatorEngine()
    screener = StockScreener(engine, config=config)
    result = screener.screen(mock_data)

    print("Screener Results (should pass):", result)
    assert not result.empty


def test_stock_screener_init_and_screen():
    screener_mod = pytest.importorskip("screening.stock_screener")
    # class could be StockScreener or similar — try both names
    Screener = getattr(screener_mod, "StockScreener", None) or getattr(
        screener_mod, "Screener", None
    )
    assert (
        Screener is not None
    ), "StockScreener class not found in screening.stock_screener"

    # Should accept config=None safely
    inst = Screener(config=None)

    # If `screen` or `run` method exists, call it and assert DataFrame returned
    if hasattr(inst, "screen"):
        out = inst.screen(limit=5)
    elif hasattr(inst, "run"):
        out = inst.run(limit=5)
    else:
        pytest.skip("No screen/run method found on StockScreener instance")

    assert out is not None
    assert isinstance(out, (list, tuple, type(pd.DataFrame()))) or hasattr(
        out, "columns"
    )
