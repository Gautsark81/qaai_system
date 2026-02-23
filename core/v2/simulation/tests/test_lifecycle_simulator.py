from core.v2.simulation.lifecycle_simulator import LifecycleSimulator
from core.v2.simulation.contracts import CapitalSnapshot, LifecycleDecision


def test_kill_on_large_drawdown():
    sim = LifecycleSimulator()

    snap = CapitalSnapshot(
        starting_capital=1000,
        ending_capital=600,
        max_drawdown=0.4,
        pnl=-400,
    )

    outcome = sim.evaluate(snap)
    assert outcome.decision == LifecycleDecision.KILL
