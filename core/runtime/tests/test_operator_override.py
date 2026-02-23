import time
import pytest
from core.runtime.operator_override import OperatorOverride, OperatorOverrideRegistry


def test_operator_override_requires_reason_and_scope():
    registry = OperatorOverrideRegistry()

    with pytest.raises(ValueError):
        registry.register(OperatorOverride("", "ALL", time.time() + 10))


def test_operator_override_expires():
    registry = OperatorOverrideRegistry()

    override = OperatorOverride(
        reason="Manual emergency",
        scope="execution",
        expires_at=time.time() + 0.01,
    )

    registry.register(override)
    time.sleep(0.02)

    assert registry.active_overrides() == []
