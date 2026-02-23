def export_telemetry(telemetry):
    """
    For forensic & compliance export.
    """
    return {
        "strategy_id": telemetry.strategy_id,
        "health": [h.__dict__ for h in telemetry.health],
        "decay": [d.__dict__ for d in telemetry.decay],
        "state": [s.__dict__ for s in telemetry.state],
    }
