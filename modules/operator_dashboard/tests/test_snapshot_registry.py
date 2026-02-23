# modules/operator_dashboard/tests/test_snapshot_registry.py

import pytest
from dataclasses import FrozenInstanceError

from modules.operator_dashboard.registry import DashboardSnapshotRegistry
from core.strategy_factory.registry import StrategyRegistry
from core.live_trading.status import ExecutionStatus


def test_dashboard_snapshot_is_immutable():
    registry = DashboardSnapshotRegistry()
    snapshot = registry.build()

    with pytest.raises(FrozenInstanceError):
        snapshot.timestamp = None


def test_snapshot_is_deterministic():
    registry = DashboardSnapshotRegistry()

    snap1 = registry.build()
    snap2 = registry.build()

    assert snap1.system == snap2.system
    assert snap1.capital == snap2.capital
    assert snap1.regime == snap2.regime
    assert snap1.strategies == snap2.strategies


def test_registry_does_not_mutate_core_state():
    core_registry = StrategyRegistry.global_instance()
    before = dict(core_registry.all())

    dashboard_registry = DashboardSnapshotRegistry()
    dashboard_registry.build()

    after = core_registry.all()

    assert before.keys() == after.keys()


def test_canary_overlay_does_not_change_lifecycle():
    registry = DashboardSnapshotRegistry()
    snapshot = registry.build()

    for strategy in snapshot.strategies.values():
        if strategy.execution_status != ExecutionStatus.ACTIVE:
            assert strategy.state in {"LIVE", "PAPER"}


def test_snapshot_structure_complete():
    snapshot = DashboardSnapshotRegistry().build()

    assert snapshot.system is not None
    assert snapshot.capital is not None
    assert snapshot.regime is not None
    assert isinstance(snapshot.strategies, dict)
    assert snapshot.alerts is not None
    assert snapshot.explainability is not None
