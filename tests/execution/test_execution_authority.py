# tests/execution/test_execution_authority.py

import pytest

from core.execution.execution_authority import (
    ExecutionAuthority,
    AuthorityState,
)


# ------------------------------------------------------------
# 1️⃣ Freeze on Capital Breach
# ------------------------------------------------------------

def test_authority_freezes_on_capital_breach():
    authority = ExecutionAuthority()

    authority.freeze("GLOBAL_CAP_BREACH")

    state = authority.get_state()

    assert state.safe_mode is True
    assert state.frozen is True
    assert "GLOBAL_CAP_BREACH" in state.reason


# ------------------------------------------------------------
# 2️⃣ Freeze is Idempotent
# ------------------------------------------------------------

def test_freeze_is_idempotent():
    authority = ExecutionAuthority()

    authority.freeze("FIRST")
    authority.freeze("SECOND")

    state = authority.get_state()

    # First reason must persist
    assert state.reason == "FIRST"
    assert state.frozen is True


# ------------------------------------------------------------
# 3️⃣ Clear Only Allowed Manually
# ------------------------------------------------------------

def test_manual_clear_restores_execution():
    authority = ExecutionAuthority()

    authority.freeze("TEST")
    authority.manual_clear()

    state = authority.get_state()

    assert state.frozen is False
    assert state.safe_mode is False


# ------------------------------------------------------------
# 4️⃣ Cannot Execute While Frozen
# ------------------------------------------------------------

def test_block_execution_when_frozen():
    authority = ExecutionAuthority()

    authority.freeze("BROKER_TIMEOUT")

    decision = authority.validate_execution_allowed()

    assert decision is False


# ------------------------------------------------------------
# 5️⃣ Execution Allowed When Healthy
# ------------------------------------------------------------

def test_execution_allowed_when_not_frozen():
    authority = ExecutionAuthority()

    decision = authority.validate_execution_allowed()

    assert decision is True