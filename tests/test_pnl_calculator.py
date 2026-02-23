from qaai_system.infra.pnl_calculator import PnLCalculator


def test_compute_trade_pnl_closed_buy():
    calc = PnLCalculator(account_equity=100000)
    trade = {
        "symbol": "RELIANCE",
        "side": "BUY",
        "entry_price": 100,
        "exit_price": 110,
        "quantity": 10,
        "status": "closed",
        "strategy_id": "alpha_v1",
    }
    pnl = calc.compute_trade_pnl(trade)
    assert pnl["realized"] == 100.0
    assert pnl["total_pnl"] == 100.0


def test_compute_trade_pnl_open_sell():
    calc = PnLCalculator(account_equity=100000)
    trade = {
        "symbol": "INFY",
        "side": "SELL",
        "entry_price": 200,
        "quantity": 5,
        "status": "open",
        "mark_price": 190,
    }
    pnl = calc.compute_trade_pnl(trade)
    assert pnl["unrealized"] == 50.0  # short gains when price falls


def test_portfolio_and_summary():
    calc = PnLCalculator(account_equity=100000)
    trades = [
        {
            "symbol": "AAPL",
            "side": "BUY",
            "entry_price": 100,
            "exit_price": 120,
            "quantity": 10,
            "status": "closed",
        },
        {
            "symbol": "TSLA",
            "side": "SELL",
            "entry_price": 200,
            "exit_price": 210,
            "quantity": 5,
            "status": "closed",
        },
    ]
    df = calc.compute_portfolio_pnl(trades)
    assert not df.empty
    summary = calc.summarize_portfolio(trades)
    assert "total_pnl" in summary
    assert summary["num_trades"] == 2
