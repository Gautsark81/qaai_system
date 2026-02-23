# tests/unit/test_risk_manager.py
import pytest
import time

from qaai_system.execution.risk_manager import RiskManager, RiskViolation

def test_is_allowed_respects_global_limit():
    rm = RiskManager({"starting_cash": 100000.0, "max_position_size_pct": 0.001})  # global limit = 100
    # current pos 0, trying to buy 101 should be disallowed
    assert rm.is_allowed("NSE:ABC", 101) is False
    assert rm.is_allowed("NSE:ABC", 100) is True
    # negative (sell) beyond -100 should also be disallowed if symmetric exposure applies
    rm.set_position("NSE:ABC", 0)
    assert rm.is_allowed("NSE:ABC", -101) is False

def test_per_symbol_limit_overrides_global():
    rm = RiskManager({"starting_cash": 100000.0, "max_position_size_pct": 0.001, "per_symbol_limits": {"NSE:ABC": 10}})
    assert rm.is_allowed("NSE:ABC", 11) is False
    assert rm.is_allowed("NSE:ABC", 10) is True
    # other symbol uses global
    assert rm.is_allowed("NSE:XYZ", 50) is True
    assert rm.is_allowed("NSE:XYZ", 101) is False

def test_reservations_block_subsequent_orders():
    rm = RiskManager({"starting_cash": 10000.0, "max_position_size_pct": 0.001})  # global limit = 10
    # reserve 6 units for pending order
    assert rm.can_place("NSE:ABC", 6, reservation_id="r1", auto_reserve=True) is True
    # another ask for 5 should be denied because 6+5 > 10
    assert rm.can_place("NSE:ABC", 5) is False
    # releasing reservation frees capacity
    rm.release_reservation("r1")  # compatibility call: release by reservation_id
    assert rm.can_place("NSE:ABC", 5) is True

def test_reservation_ttl_expires():
    rm = RiskManager({"starting_cash": 10000.0, "max_position_size_pct": 0.001})
    rm.reservation_ttl = 0.1  # seconds
    rm.can_place("NSE:ABC", 8, reservation_id="r2", auto_reserve=True)
    assert rm.can_place("NSE:ABC", 3) is False
    time.sleep(0.15)
    assert rm.can_place("NSE:ABC", 3) is True

def test_position_getter_integration_mode():
    def getter(sym):
        if sym == "NSE:ABC":
            return 9
        return 0
    # changed starting_cash from 100.0 -> 10.0 so global limit = 10 and 9 + 2 = 11 => blocked
    rm = RiskManager({"starting_cash": 10.0, "max_position_size_pct": 1.0})  # global limit = 10
    rm.position_getter = getter
    assert rm.is_allowed("NSE:ABC", 2) is False
    assert rm.is_allowed("NSE:ABC", 1) is True

def test_metrics_callback_called():
    events = []
    def metrics_cb(event, payload):
        events.append((event, payload))
    rm = RiskManager({"starting_cash": 10000.0, "max_position_size_pct": 0.001})
    rm.metrics_callback = metrics_cb
    rm.can_place("NSE:ABC", 5, reservation_id="r3", auto_reserve=True)
    found = [e for e in events if e[0].startswith("reservation.") or e[0] == "exceeds_check"]
    assert len(found) >= 1

def test_dump_state_contains_expected_keys():
    rm = RiskManager({"starting_cash": 5000.0, "max_position_size_pct": 0.002, "per_symbol_limits": {"NSE:ABC": 10}})
    rm.set_position("NSE:ABC", 1)
    rm.reserve("rid", "NSE:ABC", 2)
    state = rm.dump_state()
    assert "positions" in state
    assert "reservations" in state
    assert "max_position" in state
    assert state["per_symbol_limits"].get("NSE:ABC") == 10
