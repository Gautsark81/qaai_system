from core.operator_dashboard.contracts.system_health import SystemHealthView
from core.state.system_state import SystemState
from core.safety.kill_switch import KillSwitch


def load_system_health() -> SystemHealthView:
    state = SystemState.current()
    kill = KillSwitch(scope="global")

    return SystemHealthView(
        system_state=state.state,
        market_session=state.market_session,

        data_feeds_ok=state.data_feeds_ok,
        broker_connected=state.broker_connected,

        global_kill_switch=kill.is_armed(),
        active_incidents=state.active_incidents,
    )
