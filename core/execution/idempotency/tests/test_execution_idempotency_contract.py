import pytest

from core.execution.idempotency.contracts import ExecutionIdempotencyKey


def test_idempotency_key_is_deterministic():
    key1 = ExecutionIdempotencyKey(
        execution_intent_id="intent-1",
        strategy_id="strat-A",
        symbol="RELIANCE",
        side="BUY",
        quantity=100,
        pricing_mode="LIMIT",
        price=2500.0,
        market_session="OPEN",
    )

    key2 = ExecutionIdempotencyKey(
        execution_intent_id="intent-1",
        strategy_id="strat-A",
        symbol="RELIANCE",
        side="BUY",
        quantity=100,
        pricing_mode="LIMIT",
        price=2500.0,
        market_session="OPEN",
    )

    assert key1.hash() == key2.hash()


def test_idempotency_key_changes_on_quantity_change():
    base = ExecutionIdempotencyKey(
        execution_intent_id="intent-1",
        strategy_id="strat-A",
        symbol="INFY",
        side="SELL",
        quantity=50,
        pricing_mode="MARKET",
        price=None,
        market_session="OPEN",
    )

    modified = ExecutionIdempotencyKey(
        execution_intent_id="intent-1",
        strategy_id="strat-A",
        symbol="INFY",
        side="SELL",
        quantity=60,  # changed
        pricing_mode="MARKET",
        price=None,
        market_session="OPEN",
    )

    assert base.hash() != modified.hash()


def test_idempotency_key_is_json_stable():
    key = ExecutionIdempotencyKey(
        execution_intent_id="intent-x",
        strategy_id="strat-x",
        symbol="TCS",
        side="BUY",
        quantity=10,
        pricing_mode="MARKET",
        price=None,
        market_session="PREOPEN",
    )

    json1 = key.to_canonical_json()
    json2 = key.to_canonical_json()

    assert json1 == json2


def test_string_representation_is_hash():
    key = ExecutionIdempotencyKey(
        execution_intent_id="i",
        strategy_id="s",
        symbol="SBIN",
        side="BUY",
        quantity=1,
        pricing_mode="MARKET",
        price=None,
        market_session="OPEN",
    )

    assert str(key) == key.hash()
