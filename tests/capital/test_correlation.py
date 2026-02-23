from qaai_system.capital.correlation import apply_correlation_penalty


def test_correlation_penalty():
    assert apply_correlation_penalty(1.0, True) == 0.5
