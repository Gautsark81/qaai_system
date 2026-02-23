from enum import Enum


class RunState(str, Enum):
    CREATED = "created"
    ACTIVE = "active"
    HALTED = "halted"
    COMPLETED = "completed"
    FAILED = "failed"


ALLOWED_TRANSITIONS = {
    RunState.CREATED: {RunState.ACTIVE},
    RunState.ACTIVE: {RunState.HALTED, RunState.COMPLETED, RunState.FAILED},
    RunState.HALTED: {RunState.ACTIVE, RunState.COMPLETED},
    RunState.COMPLETED: set(),
    RunState.FAILED: set(),
}
