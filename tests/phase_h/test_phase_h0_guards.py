# tests/phase_h/test_phase_h0_guards.py

import inspect

import modules.strategies.base as strategies_base
import modules.execution.plan_builder as plan_builder
import modules.order_manager.manager as order_manager


FORBIDDEN_FLAG_USAGE = (
    "LIVE_TRADING",
    "DRY_RUN",
    "AUDIT_ENABLED",
    "METRICS_ENABLED",
)


def assert_no_flag_usage(module):
    src = inspect.getsource(module)
    for flag in FORBIDDEN_FLAG_USAGE:
        assert flag not in src, f"{flag} used in {module.__name__}"


def test_strategies_do_not_use_runtime_flags():
    assert_no_flag_usage(strategies_base)


def test_execution_does_not_use_runtime_flags():
    assert_no_flag_usage(plan_builder)


def test_order_manager_does_not_use_runtime_flags():
    assert_no_flag_usage(order_manager)
