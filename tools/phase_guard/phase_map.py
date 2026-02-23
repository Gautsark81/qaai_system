from pathlib import Path

# Authoritative phase boundaries
PHASES = {
    "11": [
        Path("core/telemetry"),
        Path("core/logging"),
        Path("core/runtime"),
    ],
    "12": [
        Path("core/safety"),
        Path("core/incidents"),
    ],
}

FROZEN_PHASES = {"11"}
