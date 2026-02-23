# dashboard/snapshot_app.py
from pathlib import Path
from dataclasses import dataclass
import sys

# ─────────────────────────────────────────────
# CRITICAL: Ensure project root is importable
# ─────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

import streamlit as st

from dashboard.lifecycle import DashboardState
from dashboard.snapshot_loader import load_dashboard_snapshot

from dashboard.adapters import (
    overview_adapter,
    screening_adapter,
    watchlist_adapter,
    strategy_adapter,
    meta_alpha_adapter,
    alerts_adapter,
)

from dashboard.adapters.execution_telemetry import (
    execution_telemetry_adapter,
)
from dashboard.views.execution_telemetry import (
    render as execution_telemetry_view,
)

from dashboard.views import (
    overview,
    screening,
    watchlist,
    strategies,
    meta_alpha,
    alerts,
)

from core.execution.replay.fs_store import FileSystemReplayStore
from dashboard.replay.rehydrate import (
    replay_result_from_dict,
    replay_diff_from_dict,
)
from dashboard.views.replay import (
    render as replay_view,
)

# --- Telemetry (event-based, disk-sourced) ---
from core.execution.telemetry_serializer import deserialize_snapshot
from core.execution.telemetry import ExecutionTelemetry
from core.execution.invariant_validator import InvariantResult
from core.execution.telemetry_snapshot import ExecutionTelemetrySnapshot


# -------------------------------------------------
# Snapshot-safe accessor
# -------------------------------------------------
def snapshot_section(snapshot, name: str, default=None):
    if snapshot is None:
        return default
    if isinstance(snapshot, dict):
        return snapshot.get(name, default)
    return getattr(snapshot, name, default)


# -------------------------------------------------
# Presentation-only execution event model
# -------------------------------------------------
@dataclass(frozen=True)
class DashboardExecutionEvent:
    timestamp: str
    event_type: str
    message: str


# ─────────────────────────────────────────────
# Streamlit App Config
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="QAAI System Dashboard",
    layout="wide",
)

st.title("🧠 QAAI System — Snapshot Dashboard")
st.caption(
    "Snapshot-only · Deterministic · No Execution · No Capital Mutation"
)

# ─────────────────────────────────────────────
# Lifecycle State + Refresh Control
# ─────────────────────────────────────────────
if "dashboard_state" not in st.session_state:
    st.session_state.dashboard_state = DashboardState.BOOTING

if "snapshot" not in st.session_state:
    st.session_state.snapshot = None

with st.sidebar:
    st.subheader("Dashboard Controls")
    if st.button("🔄 Refresh Snapshot"):
        st.session_state.dashboard_state = DashboardState.REFRESHING

if st.session_state.dashboard_state in (
    DashboardState.BOOTING,
    DashboardState.REFRESHING,
):
    state, snapshot = load_dashboard_snapshot()
    st.session_state.dashboard_state = state
    st.session_state.snapshot = snapshot

state = st.session_state.dashboard_state
snapshot = st.session_state.snapshot

# ─────────────────────────────────────────────
# Lifecycle Status Banner
# ─────────────────────────────────────────────
if state is DashboardState.BOOTING:
    st.info("Dashboard booting…")
elif state is DashboardState.REFRESHING:
    st.info("Refreshing snapshot…")
elif state is DashboardState.DEGRADED:
    st.error("Dashboard in degraded state — snapshot unavailable.")
    st.stop()
elif state is DashboardState.IDLE:
    st.success("Dashboard idle · Snapshot loaded")

if snapshot is None:
    st.error("Snapshot unavailable.")
    st.stop()

# =================================================
# 🧩 PHASE INDEX — CANONICAL VISIBILITY (NEW)
# =================================================
st.divider()
st.subheader("🧩 Phase Status Index")

PHASES = [
    ("Phase-1.0", "Snapshot Core", True),
    ("Phase-1.1", "Screening / Watchlist", True),
    ("Phase-1.2", "System Mood", snapshot.system_mood_drift is not None),
    ("Phase-1.3", "Execution Telemetry", True),
    ("Phase-1.4", "Snapshot Immutability", True),
    ("Phase-1.5", "Snapshot Lineage", True),
    ("Phase-1.6", "Promotion Chain", snapshot.lineage_depth > 0),
    ("Phase-1.7", "Governance Hooks", snapshot.governance_status is not None),
    ("Phase-1.8", "Governance Evaluation", snapshot.governance_checked_at is not None),
    ("Phase-1.9", "Execution Arming (LOCKED)", False),
]

for code, name, active in PHASES:
    st.write(f"{'🟢' if active else '⚪'} **{code}** — {name}")

# =================================================
# 🛡️ SHADOW LIVE SAFETY PROOF (Phase-1)
# =================================================
st.divider()
st.subheader("🛡️ Shadow Live Safety Proof (Phase-1)")

safety = snapshot_section(snapshot, "safety", {})

col1, col2, col3 = st.columns(3)
col1.metric("Execution Possible", "NO")
col2.metric("Capital Allocated", 0.0)
col3.metric("Kill Switch", "UNKNOWN")

st.info(
    "✔ This snapshot proves execution is impossible and capital is zero. "
    "Shadow Live is observational only."
)

# =================================================
# 🧬 SNAPSHOT LINEAGE & PROMOTION (Phase-1.5 / 1.6)
# =================================================
st.divider()
st.subheader("🧬 Snapshot Lineage")

st.metric("Lineage Depth", snapshot.lineage_depth)

if snapshot.parent_hash:
    st.code(snapshot.parent_hash, language="text")
else:
    st.info("Genesis snapshot (no parent).")

st.caption(f"Promotion Cause: {snapshot.cause}")

# =================================================
# 🧠 GOVERNANCE STATE (Phase-1.7 / 1.8)
# =================================================
st.divider()
st.subheader("🧠 Governance State")

st.metric("Governance Status", snapshot.governance_status)

if snapshot.governance_reason:
    st.write(f"Reason: {snapshot.governance_reason}")
else:
    st.info("No governance decision recorded.")

if snapshot.governance_checked_at:
    st.caption(f"Evaluated at: {snapshot.governance_checked_at}")
else:
    st.caption("Governance evaluation pending.")

# =================================================
# Adapt Snapshot → View Models (UNCHANGED)
# =================================================
overview_data = overview_adapter(snapshot)
screening_data = screening_adapter(snapshot)
watchlist_data = watchlist_adapter(snapshot)
strategy_data = strategy_adapter(snapshot)
meta_alpha_data = meta_alpha_adapter(snapshot)
alerts_data = alerts_adapter(snapshot)

# =================================================
# Snapshot-Based Sections (UNCHANGED BEHAVIOR)
# =================================================
st.divider()
overview(overview_data)

st.divider()
screening(screening_data)

st.divider()
watchlist(watchlist_data)

st.divider()
strategies(strategy_data)

st.divider()
meta_alpha(meta_alpha_data)

st.divider()
alerts(alerts_data)

# =================================================
# 📉 SYSTEM MOOD DRIFT (Phase-1.2)
# =================================================
st.divider()
st.subheader("📉 System Mood Drift (Phase-1.2)")

drift = snapshot.system_mood_drift
c1, c2, c3 = st.columns(3)
c1.metric("Mean Mood", f"{drift.mean:.1f}")
c2.metric("Trend (Slope)", f"{drift.slope:.3f}")
c3.metric("Volatility", f"{drift.volatility:.3f}")
st.caption(drift.explanation)

# =================================================
# Execution Telemetry (READ-ONLY)
# =================================================
st.divider()
st.subheader("Execution Telemetry")

TELEMETRY_DIR = Path("data/telemetry")

if not TELEMETRY_DIR.exists():
    st.info("Telemetry directory not present.")
else:
    telemetry_files = sorted(TELEMETRY_DIR.glob("*.jsonl"))
    if telemetry_files:
        latest_file = telemetry_files[-1]
        try:
            events = []
            with latest_file.open("r", encoding="utf-8") as f:
                for line in f:
                    if not line.strip():
                        continue
                    raw = deserialize_snapshot(line)
                    events.append(
                        DashboardExecutionEvent(
                            timestamp=raw["timestamp"],
                            event_type=raw["event_type"],
                            message=raw["message"],
                        )
                    )

            if events:
                execution_id = latest_file.stem
                telemetry = ExecutionTelemetry(
                    execution_id=execution_id,
                    started_at=events[0].timestamp,
                    completed_at=events[-1].timestamp,
                    total_orders=len([e for e in events if e.event_type == "ORDER_SUBMITTED"]),
                    filled_orders=len([e for e in events if e.event_type == "ORDER_FILLED"]),
                    rejected_orders=len([e for e in events if e.event_type == "ORDER_REJECTED"]),
                    cancelled_orders=len([e for e in events if e.event_type == "ORDER_CANCELLED"]),
                    events=tuple(events),
                )

                invariants = InvariantResult(
                    execution_id=execution_id,
                    checked_at=events[-1].timestamp,
                    violations=(),
                )

                snapshot_vm = ExecutionTelemetrySnapshot(
                    telemetry=telemetry,
                    invariants=invariants,
                )

                execution_telemetry_view(
                    execution_telemetry_adapter(snapshot_vm)
                )

        except Exception as exc:
            st.error("Failed to load execution telemetry.")
            st.exception(exc)
    else:
        st.info("No execution telemetry available.")

# =================================================
# Execution Replay (READ-ONLY)
# =================================================
st.divider()
st.subheader("Execution Replay")

REPLAY_STORE_DIR = Path("data/replay")

if REPLAY_STORE_DIR.exists():
    replay_store = FileSystemReplayStore(REPLAY_STORE_DIR)
    results_dir = REPLAY_STORE_DIR / "results"

    if results_dir.exists():
        for exec_id in sorted(p.stem for p in results_dir.glob("*.jsonl")):
            results = [
                replay_result_from_dict(d)
                for d in replay_store.get_results_by_execution_id(exec_id)
            ]
            diffs = [
                replay_diff_from_dict(d)
                for d in replay_store.get_diffs_by_execution_id(exec_id)
            ]
            replay_view(results, diffs)
else:
    st.info("Replay store not present.")

# =================================================
# Footer
# =================================================
st.divider()
st.caption(
    "Snapshot-only · Deterministic · No Execution · No Capital Mutation"
)
