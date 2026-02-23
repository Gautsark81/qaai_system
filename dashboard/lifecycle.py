from enum import IntEnum


class DashboardState(IntEnum):
    BOOTING = -2        # Streamlit app just started
    INIT = -1           # Session initialized, no snapshot yet
    REFRESHING = 0      # Fetching / recomputing snapshot
    DEGRADED = 1        # Fallback snapshot (errors, partial data)
    IDLE = 2            # Healthy steady-state snapshot
