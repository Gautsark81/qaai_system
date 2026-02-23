from enum import Enum


class CanaryMode(str, Enum):
    OFF = "OFF"
    PAPER = "PAPER"
    LIVE = "LIVE"
