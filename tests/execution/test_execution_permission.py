from datetime import datetime

import pytest

from core.execution.contracts.execution_permission import ExecutionPermission


def test_permission_allows_execution():
    permission = ExecutionPermission(
        strategy_id="s1",
        allowed=True,
        issued_at=datetime.utcnow(),
        allocated_capital=1000.0,
        gate_reasons=["capital-ok", "risk-ok"],
    )

    # Should not raise
    permission.assert_allowed()


def test_permission_blocks_execution():
    permission = ExecutionPermission(
        strategy_id="s1",
        allowed=False,
        issued_at=datetime.utcnow(),
        allocated_capital=0.0,
        gate_reasons=["capital-insufficient"],
    )

    with pytest.raises(PermissionError) as exc:
        permission.assert_allowed()

    assert "Execution denied" in str(exc.value)
    assert "capital-insufficient" in str(exc.value)


def test_permission_is_immutable():
    permission = ExecutionPermission(
        strategy_id="s1",
        allowed=True,
        issued_at=datetime.utcnow(),
    )

    with pytest.raises(Exception):
        permission.allowed = False


def test_permission_serializable_fields():
    permission = ExecutionPermission(
        strategy_id="s1",
        allowed=True,
        issued_at=datetime.utcnow(),
        allocated_capital=500.0,
        gate_reasons=["ok"],
    )

    assert isinstance(permission.strategy_id, str)
    assert isinstance(permission.allowed, bool)
    assert isinstance(permission.issued_at, datetime)
    assert isinstance(permission.gate_reasons, list)
