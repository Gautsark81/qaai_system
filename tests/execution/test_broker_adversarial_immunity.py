# tests/execution/test_broker_adversarial_immunity.py

import time
import pytest

from core.execution.broker_guard import (
    BrokerGuard,
    BrokerDecision,
)


# ------------------------------------------------------------
# 1️⃣ Latency Classification
# ------------------------------------------------------------

def test_latency_normal():
    guard = BrokerGuard(max_latency_ms=500)

    decision = guard.validate_latency(latency_ms=200)

    assert decision.allowed is True
    assert decision.freeze is False


def test_latency_exceeds_threshold():
    guard = BrokerGuard(max_latency_ms=300)

    decision = guard.validate_latency(latency_ms=800)

    assert decision.freeze is True
    assert "LATENCY" in decision.reason


# ------------------------------------------------------------
# 2️⃣ Missing ACK Timeout
# ------------------------------------------------------------

def test_ack_timeout_freezes():
    guard = BrokerGuard(ack_timeout_seconds=1)

    order_id = "abc123"
    guard.register_order(order_id)

    time.sleep(1.2)

    decision = guard.validate_ack(order_id)

    assert decision.freeze is True
    assert "ACK_TIMEOUT" in decision.reason


def test_ack_received_allows():
    guard = BrokerGuard(ack_timeout_seconds=2)

    order_id = "xyz789"
    guard.register_order(order_id)

    guard.mark_ack_received(order_id)

    decision = guard.validate_ack(order_id)

    assert decision.allowed is True


# ------------------------------------------------------------
# 3️⃣ Slippage Anomaly Guard
# ------------------------------------------------------------

def test_slippage_within_bounds():
    guard = BrokerGuard(max_slippage_pct=0.5)

    decision = guard.validate_slippage(
        expected_price=100,
        executed_price=100.3,
    )

    assert decision.allowed is True


def test_slippage_exceeds_threshold():
    guard = BrokerGuard(max_slippage_pct=0.5)

    decision = guard.validate_slippage(
        expected_price=100,
        executed_price=102,
    )

    assert decision.freeze is True
    assert "SLIPPAGE" in decision.reason


# ------------------------------------------------------------
# 4️⃣ Heartbeat Failure
# ------------------------------------------------------------

def test_heartbeat_valid():
    guard = BrokerGuard(heartbeat_timeout_seconds=2)

    guard.update_heartbeat()

    decision = guard.validate_heartbeat()

    assert decision.allowed is True


def test_heartbeat_timeout_freezes():
    guard = BrokerGuard(heartbeat_timeout_seconds=1)

    guard.update_heartbeat()
    time.sleep(1.2)

    decision = guard.validate_heartbeat()

    assert decision.freeze is True
    assert "HEARTBEAT" in decision.reason