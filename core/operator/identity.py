# core/operator/identity.py
from dataclasses import dataclass


@dataclass(frozen=True)
class OperatorIdentity:
    operator_id: str
    display_name: str
    role: str  # e.g. "trader", "risk", "admin"
