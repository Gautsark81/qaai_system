import pytest

from qaai_system.model_ops.capital import CapitalLadder, CapitalStep


def test_ladder_accepts_multiple_steps():
    ladder = CapitalLadder([
        CapitalStep("canary_5", 0.05),
        CapitalStep("canary_15", 0.15),
        CapitalStep("full", 1.0),
    ])

    step = ladder.step(1)
    assert step.name == "canary_15"
    assert step.weight == 0.15


def test_ladder_rejects_empty_steps():
    with pytest.raises(ValueError):
        CapitalLadder([])


def test_ladder_rejects_invalid_weights():
    with pytest.raises(ValueError):
        CapitalLadder([
            CapitalStep("bad", -0.1),
        ])

    with pytest.raises(ValueError):
        CapitalLadder([
            CapitalStep("too_big", 1.5),
        ])
