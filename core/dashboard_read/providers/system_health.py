# core/dashboard_read/providers/system_health.py

from core.dashboard_read.providers.state_types import SystemHealthState
from core.dashboard_read.providers._sources import system_health as system_health_source


def build_system_health() -> SystemHealthState:
    """
    Build system health state.

    This provider performs no logic.
    It only copies values from source.
    """

    broker_status = system_health_source.read_broker_status()
    data_feeds = system_health_source.read_data_feed_health()
    clock_status = system_health_source.read_clock_status()
    system_flags = system_health_source.read_system_flags()

    # Provider must not compute.
    # Only structural copying allowed.

    return SystemHealthState(
        broker_status=broker_status,
        data_feeds=data_feeds,
        clock_status=clock_status,
        system_flags=system_flags,
    )