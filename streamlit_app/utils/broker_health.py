import streamlit as st
from infra.broker_factory import get_broker_adapter


@st.cache_resource
def get_broker():
    """Initialize broker adapter once per session."""
    try:
        return BrokerAdapter()
    except Exception:
        return None


@st.cache_resource
def get_broker_ping():
    """
    Run a broker connectivity check.
    Returns:
        (ok: bool, message: str)
    """
    try:
        broker = get_broker_adapter()
        if broker and hasattr(broker, "ping_broker"):
            ok = broker.ping_broker()
            if ok:
                return True, "Broker ping OK ✅"
            else:
                return False, "Broker ping failed ❌"
        return False, "No broker adapter available"
    except Exception as e:
        return False, f"Broker ping error: {e}"


def render_broker_health():
    """Render broker health in sidebar with refresh option."""
    # Add refresh button
    if st.sidebar.button("🔄 Refresh Broker Status"):
        get_broker_ping.clear()  # clear cached ping
        st.rerun()  # re-run Streamlit script

    ok, msg = get_broker_ping()
    if ok:
        st.sidebar.success(f"✅ Broker healthy ({msg})")
    else:
        st.sidebar.warning(f"⚠️ Broker issue: {msg}")
