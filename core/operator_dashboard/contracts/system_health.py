from dataclasses import dataclass


@dataclass(frozen=True)
class SystemHealthView:
    system_state: str
    market_session: str

    data_feeds_ok: bool
    broker_connected: bool

    global_kill_switch: bool
    active_incidents: int
