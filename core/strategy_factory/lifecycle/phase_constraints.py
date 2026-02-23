from core.strategy_factory.exceptions import ExecutionNotAllowed


def assert_execution_allowed(*, phase: str):
    """
    Phase-B and Phase-9 are advisory only.
    """
    if phase.upper() in {"B", "PHASE_B", "PHASE9"}:
        raise ExecutionNotAllowed(
            "Execution forbidden in advisory / lifecycle autonomy phases"
        )
