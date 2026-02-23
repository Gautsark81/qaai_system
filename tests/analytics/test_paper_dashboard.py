from pathlib import Path
from analytics.paper_dashboard import PaperPerformanceDashboard


def test_equity_curve_build(tmp_path):
    dash = PaperPerformanceDashboard(tmp_path)

    dash.record_trade({"timestamp": "2024-01-01", "pnl": 100})
    dash.record_trade({"timestamp": "2024-01-02", "pnl": -50})

    eq = dash.build_equity_curve(1000)
    assert eq.iloc[-1]["equity"] == 1050
