from core.v2.simulation.capital_simulator import CapitalSimulator


def test_capital_replay_and_drawdown():
    sim = CapitalSimulator()

    snapshot = sim.replay(
        starting_capital=1000,
        pnl_series=[100, -50, 200, -400],
    )

    assert snapshot.ending_capital == 850
    assert snapshot.max_drawdown > 0
