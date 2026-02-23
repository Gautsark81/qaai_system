# tests/test_signal_tp_sl.py
import pytest

# Prefer importorskip for optional heavy deps or non-present modules
# This avoids pytest.skip at module-level which needs allow_module_level=True
# and makes the test file safe to import even if the signal module is missing.

# Try to import the project's signal_engine; skip the whole module if not present.
signal_mod = pytest.importorskip(
    "execution.signal_engine", reason="execution.signal_engine not available"
)

# If project layout uses package name, try that too
if signal_mod is None:
    signal_mod = pytest.importorskip(
        "qaai_system.execution.signal_engine",
        reason="qaai_system.execution.signal_engine not available",
    )

compute_sl = getattr(signal_mod, "compute_sl", None)
compute_new_tsl = getattr(signal_mod, "compute_new_tsl", None)
make_tp_levels = getattr(signal_mod, "make_tp_levels", None)

# If any of the helpers are missing, skip the tests
if compute_sl is None or compute_new_tsl is None or make_tp_levels is None:
    pytest.skip("signal_engine helpers not present; skipping tests", allow_module_level=True)


def test_compute_sl_loss():
    sl = compute_sl(100.0, 2.0, 98.0)
    assert sl == pytest.approx(100.0 - 1.5 * 2.0)


def test_compute_sl_profit_none():
    assert compute_sl(100.0, 2.0, 101.0) is None


def test_compute_tsl():
    new = compute_new_tsl(None, 104.0, 2.0)
    assert new == pytest.approx(104.0 - 1.0 * 2.0)


def test_tp_levels():
    tps = make_tp_levels(100.0, 97.0, multipliers=[1.0, 2.0])
    assert len(tps) == 2
    assert tps[0]["price"] == pytest.approx(100.0 + 1.0 * (100.0 - 97.0))
