from core.strategy_factory.health.ssr_engine import SSREngine


def test_ssr_basic_computation():
    ssr = SSREngine.compute(
        components={
            "performance": 0.8,
            "risk": 0.6,
            "stability": 0.7,
        }
    )

    assert 0.0 <= ssr <= 1.0
    assert round(ssr, 4) == 0.71


def test_missing_component_is_zero():
    ssr = SSREngine.compute(
        components={
            "performance": 1.0,
        }
    )

    assert ssr < 0.5  # risk + stability default to 0


def test_out_of_bounds_scores_are_clamped():
    ssr = SSREngine.compute(
        components={
            "performance": 2.0,
            "risk": -1.0,
            "stability": 0.5,
        }
    )

    assert 0.0 <= ssr <= 1.0


def test_zero_weights_return_zero():
    ssr = SSREngine.compute(
        components={"performance": 1.0},
        weights={"performance": 0.0},
    )

    assert ssr == 0.0


def test_determinism():
    c = {"performance": 0.7, "risk": 0.6, "stability": 0.8}
    assert SSREngine.compute(components=c) == SSREngine.compute(components=c)
