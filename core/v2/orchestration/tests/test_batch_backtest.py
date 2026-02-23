def test_batch_backtest_returns_results():
    from core.v2.orchestration.batch_backtest import BatchBacktester
    from core.v2.orchestration.contracts import StrategyCandidate

    bt = BatchBacktester()
    results = bt.run(
        [
            StrategyCandidate("S1", {}, "test"),
            StrategyCandidate("S2", {}, "test"),
        ]
    )

    assert len(results) == 2
    assert all(r.ssr > 0 for r in results)
