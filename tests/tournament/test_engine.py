from qaai_system.tournament.engine import StrategyTournamentEngine


def test_tournament_engine_flow(dummy_snapshots):
    engine = StrategyTournamentEngine()

    results = engine.run(
        snapshots=dummy_snapshots,
        source_stage="BACKTEST",
        target_stage="PAPER",
    )

    assert results
    assert any(r.eligible for r in results)
