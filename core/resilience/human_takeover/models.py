# core/resilience/human_takeover/models.py
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Any


class ControlAuthority(str, Enum):
    SYSTEM = "system"
    HUMAN = "human"


@dataclass(frozen=True)
class TakeoverEvent:
    authority: ControlAuthority
    reason: str
    evidence: Dict[str, Any]
