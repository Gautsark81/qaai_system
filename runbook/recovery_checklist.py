def recovery_checklist() -> list[str]:
    return [
        "state_loaded",
        "broker_reconciled",
        "positions_verified",
        "operator_approved",
        "canary_mode_only",
    ]
