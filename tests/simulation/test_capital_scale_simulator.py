from simulation.capital_scale_simulator import simulate_capital_scale


def test_capital_scale_simulation():
    steps = simulate_capital_scale(10000, 3, 1.5, 50000)
    assert steps[-1].capital <= 50000
