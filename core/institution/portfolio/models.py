# core/institution/portfolio/models.py
from dataclasses import dataclass
from typing import Dict, Any


@dataclass(frozen=True)
class Portfolio:
    """
    Logical portfolio boundary.

    NOTE:
    - No capital math
    - No execution authority
    """
    portfolio_id: str
    name: str
    metadata: Dict[str, Any]
