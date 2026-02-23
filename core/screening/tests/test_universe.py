from core.screening.universe import load_symbol_universe


def test_universe_is_deterministic():
    u1 = load_symbol_universe()
    u2 = load_symbol_universe()

    assert u1 == u2
    assert isinstance(u1, list)
    assert len(u1) > 0
    assert all(isinstance(s, str) for s in u1)
