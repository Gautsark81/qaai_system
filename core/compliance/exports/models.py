# core/compliance/exports/models.py
from dataclasses import dataclass
from typing import List, Dict, Any


@dataclass(frozen=True)
class SEBIAuditExport:
    """
    Deterministic, regulator-grade audit export.
    """
    export_id: str
    trades: List[Dict[str, Any]]
    decisions: List[Dict[str, Any]]
    explanations: List[str]
