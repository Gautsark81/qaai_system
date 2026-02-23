# tests/test_idempotent_order_manager.py
import sqlite3
import time
import pytest

from modules.execution.idempotent_order_manager import IdempotentOrderManager

def fake_sender_success(payload):
    return {"ok": True, "order_id": payload.get("client_tag", "X")}

def fake_sender_once_then_fail():
    state = {"count": 0}
    def sender(payload):
        state["count"] += 1
        if state["count"] == 1:
            return {"ok": True, "order_id": "first"}
        raise RuntimeError("downstream failure")
    return sender

def test_idempotent_basic(tmp_path):
    db = str(tmp_path / "orders.db")
    iom = IdempotentOrderManager(fake_sender_success, db)
    p = {"symbol": "ABC", "size": 1, "client_tag": "abc123"}
    r1 = iom.send_order(p)
    r2 = iom.send_order(p)
    assert r1 == r2

def test_idempotent_retries(tmp_path):
    db = str(tmp_path / "orders2.db")
    sender = fake_sender_once_then_fail()
    iom = IdempotentOrderManager(sender, db)
    p = {"symbol": "ABC", "size": 1, "client_tag": "def456"}
    # first call returns success
    r1 = iom.send_order(p, max_retries=1)
    assert r1["order_id"] == "first"
    # subsequent calls read from DB and return same
    r2 = iom.send_order(p)
    assert r2["order_id"] == "first"
