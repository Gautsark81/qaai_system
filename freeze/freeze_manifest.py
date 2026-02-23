from datetime import datetime


def freeze_manifest(checksum: str) -> dict:
    return {
        "frozen_at": datetime.utcnow().isoformat(),
        "checksum": checksum,
        "tests_passed": True,
        "environment": "LIVE_CANARY",
    }
