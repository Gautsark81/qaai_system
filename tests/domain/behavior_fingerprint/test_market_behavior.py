from datetime import timedelta
from domain.behavior_fingerprint.market_behavior import MarketInteractionFingerprint


def test_market_interaction_fingerprint():
    fp = MarketInteractionFingerprint(
        instruments=["NIFTY", "BANKNIFTY"],
        avg_holding_period=timedelta(minutes=15),
        trade_frequency_per_day=12.5,
        market_regimes={"trend", "range"},
        session_bias={"open", "close"},
    )

    assert "NIFTY" in fp.instruments
    assert fp.trade_frequency_per_day > 0
