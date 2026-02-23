def test_tournament_ranking_and_scoring():
    from core.v2.orchestration.tournament_scheduler import TournamentScheduler
    from core.v2.orchestration.contracts import StrategyCandidate, BacktestResult

    scheduler = TournamentScheduler()

    candidates = [
        StrategyCandidate("A", {}, "test"),
        StrategyCandidate("B", {}, "test"),
    ]

    backtests = [
        BacktestResult("A", ssr=0.9, pnl=1000, drawdown=100, trades=30),
        BacktestResult("B", ssr=0.6, pnl=800, drawdown=200, trades=25),
    ]

    results = scheduler.run(
        candidates=candidates,
        backtest_results=backtests,
    )

    assert results[0].alpha_score >= results[1].alpha_score
    assert results[0].verdict in {
        "STRONG_ALPHA",
        "MODERATE_ALPHA",
        "WEAK_ALPHA",
    }
