def strategy_health_snapshot(telemetry):
    """
    Read-only health endpoint.
    """
    return {
        "health_score": telemetry.last_health().health_score,
        "state": telemetry.last_state().state,
        "decay": telemetry.last_decay().level,
        "flags": telemetry.last_health().flags,
    }
