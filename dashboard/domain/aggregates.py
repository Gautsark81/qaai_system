def compute_determinism_stability(state) -> float:
    hashes = state.determinism_hashes
    if not hashes:
        return 1.0
    unique = len(set(hashes))
    total = len(hashes)
    return 1.0 - ((unique - 1) / max(1, total))


def compute_system_mood(state) -> float:
    violation_penalty = min(1.0, state.violation_rate / 5.0)
    telemetry_penalty = 1.0 - state.telemetry_completeness
    execution_penalty = 1.0 if state.execution_possible else 0.0

    mood = 100 * (
        1
        - 0.4 * violation_penalty
        - 0.3 * telemetry_penalty
        - 0.3 * execution_penalty
    )
    return max(0.0, min(100.0, mood))
