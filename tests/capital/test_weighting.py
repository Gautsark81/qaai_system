from qaai_system.capital.weighting import compute_weight


def test_weight_positive(snapshot):
    assert compute_weight(snapshot) > 0
