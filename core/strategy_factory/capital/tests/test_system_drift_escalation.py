from __future__ import annotations

import pytest

from execution.execution_reconciler import DriftRecord, DriftSeverity, DriftType
from core.strategy_factory.capital.ledger_reconciliation import (
    CapitalUsageReconciliationReport,
)
from core.strategy_factory.capital.system_drift_escalation import (
    SystemDriftEscalationEngine,
    SystemEscalationLevel,
)


# ============================================================
# HELPERS
# ============================================================

def _make_exec_drift(severity: DriftSeverity) -> DriftRecord:
    return DriftRecord(
        drift_type=DriftType.MISSING_ORDER,
        severity=severity,
        order_id="oid1",
        symbol="NIFTY",
        details={},
    )


def _capital_report(is_consistent: bool, violations=None):
    return CapitalUsageReconciliationReport(
        is_consistent=is_consistent,
        violations=violations or [],
        entry_count=1,
    )


# ============================================================
# OK CASE
# ============================================================

def test_escalation_ok():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[],
        capital_report=_capital_report(True),
        governance_violation=False,
    )

    assert report.level == SystemEscalationLevel.OK
    assert report.execution_drifts == 0
    assert report.capital_violations == 0
    assert report.governance_violation is False
    assert isinstance(report.fingerprint, str)
    assert len(report.fingerprint) == 64


# ============================================================
# WARNING CASE
# ============================================================

def test_escalation_warning_on_exec_warning():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[_make_exec_drift(DriftSeverity.WARNING)],
        capital_report=_capital_report(True),
        governance_violation=False,
    )

    assert report.level == SystemEscalationLevel.WARNING


def test_escalation_warning_on_capital_violation():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[],
        capital_report=_capital_report(False, violations=["delta_mismatch"]),
        governance_violation=False,
    )

    assert report.level == SystemEscalationLevel.CRITICAL  # inconsistent capital → CRITICAL


# ============================================================
# CRITICAL CASE
# ============================================================

def test_escalation_critical_on_exec_critical():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[_make_exec_drift(DriftSeverity.CRITICAL)],
        capital_report=_capital_report(True),
        governance_violation=False,
    )

    assert report.level == SystemEscalationLevel.CRITICAL


# ============================================================
# SYSTEM HALT CASES
# ============================================================

def test_escalation_system_halt_on_governance_violation():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[],
        capital_report=_capital_report(True),
        governance_violation=True,
    )

    assert report.level == SystemEscalationLevel.SYSTEM_HALT


def test_escalation_system_halt_on_exec_and_capital():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[_make_exec_drift(DriftSeverity.CRITICAL)],
        capital_report=_capital_report(False, violations=["negative_capital"]),
        governance_violation=False,
    )

    assert report.level == SystemEscalationLevel.SYSTEM_HALT


# ============================================================
# FINGERPRINT DETERMINISM
# ============================================================

def test_fingerprint_is_deterministic():
    engine = SystemDriftEscalationEngine()

    drifts = [_make_exec_drift(DriftSeverity.CRITICAL)]
    capital = _capital_report(False, violations=["v1"])

    r1 = engine.evaluate(
        execution_drifts=drifts,
        capital_report=capital,
        governance_violation=False,
    )

    r2 = engine.evaluate(
        execution_drifts=drifts,
        capital_report=capital,
        governance_violation=False,
    )

    # Fingerprint must match (timestamp differs but fingerprint stable)
    assert r1.fingerprint == r2.fingerprint


# ============================================================
# IMMUTABILITY
# ============================================================

def test_report_is_immutable():
    engine = SystemDriftEscalationEngine()

    report = engine.evaluate(
        execution_drifts=[],
        capital_report=_capital_report(True),
        governance_violation=False,
    )

    with pytest.raises(Exception):
        report.level = SystemEscalationLevel.CRITICAL