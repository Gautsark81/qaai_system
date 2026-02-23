from core.dashboard_read.snapshot import OpsState
from core.dashboard_read.providers._sources import ops as ops_source


def build_ops_state() -> OpsState:
    """
    Operational governance state provider.
    Copy-only.
    """

    metrics = ops_source.read_ops_metrics()

    return OpsState(
        human_control=False,
        takeover_active=False,
        succession_mode=False,
        runbook_link=None,
    )
