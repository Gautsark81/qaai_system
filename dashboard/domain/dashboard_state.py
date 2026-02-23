# dashboard/domain/dashboard_state.py

from enum import IntEnum

class DashboardState(IntEnum):
    INIT = 0
    DEGRADED = 1
    IDLE = 2
