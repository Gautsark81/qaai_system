import pandas as pd
from portfolio.simulator import PortfolioSimulator


def test_portfolio_simulator_basic():
    simulator = PortfolioSimulator(initial_cash=100000, max_allocation_per_trade=0.1)

    # Mock signal data
    signals = pd.DataFrame(
        [
            {
                "timestamp": "2023-01-01 09:15",
                "symbol": "ABC",
                "signal": "BUY",
                "price": 100,
                "confidence": 0.9,
            },
            {
                "timestamp": "2023-01-01 09:45",
                "symbol": "ABC",
                "signal": "SELL",
                "price": 110,
                "confidence": 0.9,
            },
            {
                "timestamp": "2023-01-01 10:00",
                "symbol": "XYZ",
                "signal": "BUY",
                "price": 200,
                "confidence": 0.8,
            },
            {
                "timestamp": "2023-01-01 10:30",
                "symbol": "XYZ",
                "signal": "SELL",
                "price": 180,
                "confidence": 0.8,
            },
        ]
    )

    trades, portfolio = simulator.run(signals)
    summary = simulator.summary()

    # Convert to Python float for type safety
    summary["pnl"] = float(summary["pnl"])
    summary["final_value"] = float(summary["final_value"])

    # Assertions
    assert not trades.empty
    assert not portfolio.empty
    assert "final_value" in summary
    assert isinstance(summary["pnl"], (int, float))
    assert summary["final_value"] != 100000  # Portfolio changed after trades
    assert summary["max_drawdown"] >= 0
