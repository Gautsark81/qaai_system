# File: qaai_system/execution/utils.py


def normalize_status(status: str) -> str:
    """
    Normalize order statuses into consistent UPPERCASE values
    (to match tests that expect BLOCKED, FILLED, CANCELLED, etc).
    """
    if not status:
        return "UNKNOWN"
    s = str(status).strip().lower()
    mapping = {
        "new": "SUBMITTED",
        "submitted": "SUBMITTED",
        "open": "OPEN",
        "partially_filled": "PARTIALLY_FILLED",
        "partial": "PARTIALLY_FILLED",
        "filled": "FILLED",
        "closed": "FILLED",
        "cancelled": "CANCELLED",
        "canceled": "CANCELLED",
        "rejected": "REJECTED",
        "error": "ERROR",
        "blocked": "BLOCKED",
    }
    return mapping.get(s, s.upper())
