class Phase1InvariantViolation(RuntimeError):
    pass


def assert_phase1_invariants(state):
    if state.execution_possible:
        raise Phase1InvariantViolation(
            "Execution became possible in Shadow/Paper mode"
        )

    if state.capital_allocated != 0:
        raise Phase1InvariantViolation(
            "Capital allocation detected in Phase-1"
        )

    if state.kill_switch_state != "armed":
        raise Phase1InvariantViolation(
            "Kill switch disarmed during observation"
        )
