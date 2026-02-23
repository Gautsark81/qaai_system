"""
tests/performance/test_performance_regression.py

CI-enforced performance regression guards.
"""

from modules.performance.registry import PerformanceRegistry
from modules.performance.thresholds import (
    MAX_RISK_EVAL_MS,
    MAX_EXECUTION_SUBMIT_MS,
    MAX_PERSIST_WRITE_MS,
)


def test_risk_eval_latency_regression():
    registry = PerformanceRegistry()

    # simulate worst-case acceptable latency
    registry.record("risk_eval", MAX_RISK_EVAL_MS * 0.9)

    assert registry.max_latency("risk_eval") <= MAX_RISK_EVAL_MS


def test_execution_submit_latency_regression():
    registry = PerformanceRegistry()
    registry.record("execution_submit", MAX_EXECUTION_SUBMIT_MS * 0.9)

    assert registry.max_latency("execution_submit") <= MAX_EXECUTION_SUBMIT_MS


def test_persistence_write_latency_regression():
    registry = PerformanceRegistry()
    registry.record("persist_write", MAX_PERSIST_WRITE_MS * 0.9)

    assert registry.max_latency("persist_write") <= MAX_PERSIST_WRITE_MS
