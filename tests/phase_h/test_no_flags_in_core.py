# tests/phase_h/test_no_flags_in_core.py

import inspect

import modules.strategies.base as strategies
import modules.execution.plan_builder as execution
import modules.risk.evaluator as risk


FORBIDDEN = ("LIVE_TRADING", "DRY_RUN", "AUDIT_ENABLED", "METRICS_ENABLED")


def assert_no_flags(module):
    src = inspect.getsource(module)
    for f in FORBIDDEN:
        assert f not in src, f"{f} used in {module.__name__}"


def test_strategies_clean():
    assert_no_flags(strategies)


def test_execution_clean():
    assert_no_flags(execution)


def test_risk_clean():
    assert_no_flags(risk)
