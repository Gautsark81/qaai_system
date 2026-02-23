from qaai_system.capital.caps import apply_caps


def test_caps_limit():
    assert apply_caps(0.9) == 0.25
