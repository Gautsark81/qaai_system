from qaai_system.capital.decay import apply_decay


def test_decay_freeze(snapshot):
    snapshot.max_drawdown = 1.0
    weight, status, _ = apply_decay(1.0, snapshot)
    assert weight == 0.0
    assert status == "FROZEN"
