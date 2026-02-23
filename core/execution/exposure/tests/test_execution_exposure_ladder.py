import pytest

from core.execution.exposure.ladder import (
    ExecutionExposureLadder,
    ExecutionExposureLevel,
)
from core.capital.arming.contracts import CapitalArmingState


def test_shadow_is_always_allowed():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.DISARMED
    )

    assert ladder.is_allowed(ExecutionExposureLevel.SHADOW) is True


def test_paper_requires_shadow_or_higher():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.SHADOW
    )

    assert ladder.is_allowed(ExecutionExposureLevel.PAPER) is True


def test_paper_blocked_when_capital_disarmed():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.DISARMED
    )

    assert ladder.is_allowed(ExecutionExposureLevel.PAPER) is False


def test_live_requires_live_capital_arming():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.PAPER
    )

    assert ladder.is_allowed(ExecutionExposureLevel.LIVE) is False


def test_live_allowed_only_when_live_armed():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.LIVE
    )

    assert ladder.is_allowed(ExecutionExposureLevel.LIVE) is True


def test_ladder_is_pure_and_stateless():
    ladder = ExecutionExposureLadder(
        capital_arming_state=CapitalArmingState.SHADOW
    )

    # multiple calls must not mutate anything
    assert ladder.is_allowed(ExecutionExposureLevel.PAPER) is True
    assert ladder.is_allowed(ExecutionExposureLevel.PAPER) is True
