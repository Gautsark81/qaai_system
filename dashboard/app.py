import streamlit as st
from infra.db_client import DBClient

# Optional imports
try:
    from modules.reporting.health_api import strategy_health_snapshot
except Exception:
    strategy_health_snapshot = None

try:
    from modules.live_control.kill_switch import KillSwitch
except Exception:
    KillSwitch = None


# ==========================================================
# PAGE CONFIG (FIRST RENDER LINE)
# ==========================================================

st.set_page_config(page_title="QAAI Live Dashboard", layout="wide")
st.title("📊 QAAI Live Trading Dashboard")


# ==========================================================
# DB INIT (HARDENED)
# ==========================================================

db = None
try:
    db = DBClient()
except Exception as e:
    st.error("❌ Database initialization failed")
    st.exception(e)
    st.stop()


# ==========================================================
# SECTION 1 — LIVE SIGNALS
# ==========================================================

st.header("📈 Latest Trading Signals")

try:
    signals = db.fetch_latest_signals(limit=100) or []
except Exception as e:
    st.error("Failed to load signals")
    st.exception(e)
    signals = []

if signals:
    st.dataframe(signals, use_container_width=True)
else:
    st.info("No signals available yet.")


# ==========================================================
# SECTION 2 — STRATEGY HEALTH
# ==========================================================

st.header("🧠 Strategy Health Overview")

if strategy_health_snapshot:
    try:
        strategies = db.fetch_active_strategies() or []
    except Exception as e:
        st.error("Failed to load strategies")
        st.exception(e)
        strategies = []

    if strategies:
        cols = st.columns(4)
        cols[0].markdown("**Strategy**")
        cols[1].markdown("**Health**")
        cols[2].markdown("**State**")
        cols[3].markdown("**Decay**")

        for s in strategies:
            try:
                telemetry = db.fetch_latest_telemetry(
                    strategy_id=s["strategy_id"]
                )
            except Exception:
                telemetry = None

            if not telemetry:
                continue

            snap = strategy_health_snapshot(telemetry)

            cols = st.columns(4)
            cols[0].text(s["strategy_id"][:12])
            cols[1].metric("", round(snap["health_score"], 3))
            cols[2].text(snap["state"])
            cols[3].text(snap["decay"])
    else:
        st.info("No active strategies.")
else:
    st.info("Health API not wired yet.")


# ==========================================================
# SECTION 3 — LIVE SAFETY STATUS
# ==========================================================

st.header("🚦 Live Safety Status")

col1, col2 = st.columns(2)

with col1:
    st.subheader("Kill-Switch")
    if KillSwitch:
        try:
            ks = KillSwitch()
            if ks.is_blocked(symbol="*", strategy_id="*"):
                st.error("GLOBAL KILL-SWITCH ACTIVE")
            else:
                st.success("Trading Enabled")
        except Exception as e:
            st.error("Kill-switch error")
            st.exception(e)
    else:
        st.info("Kill-switch not connected")

with col2:
    st.subheader("Circuit Breakers")
    try:
        breakers = db.fetch_circuit_status() or {}
        st.json(breakers)
    except Exception as e:
        st.error("Circuit breaker read failed")
        st.exception(e)


# ==========================================================
# SECTION 4 — AUDIT & TELEMETRY
# ==========================================================

st.header("🧾 Audit & Telemetry")

try:
    all_strategies = db.fetch_all_strategies() or []
except Exception:
    all_strategies = []

if all_strategies:
    selected_strategy = st.selectbox(
        "Select Strategy",
        options=[s["strategy_id"] for s in all_strategies],
    )

    try:
        telemetry_rows = db.fetch_telemetry_history(
            strategy_id=selected_strategy,
            limit=200,
        ) or []
    except Exception:
        telemetry_rows = []

    if telemetry_rows:
        st.dataframe(telemetry_rows, use_container_width=True)
    else:
        st.info("No telemetry yet.")
else:
    st.info("No strategies found.")


# ==========================================================
# FOOTER
# ==========================================================

st.caption(
    "QAAI System — Read-Only Operations Dashboard | "
    "Health • Decay • State • Safety • Audit"
)
