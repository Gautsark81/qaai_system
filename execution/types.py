# qaai_system/execution/types.py
"""
Execution-level shared types.

This module MUST remain dependency-free and stable.
It defines core data contracts used across router, orchestrator,
and higher-level pipelines.

DO NOT import execution logic here.
"""

from typing import Any, Dict


class ParentResponse(dict):
    """
    Canonical parent-order response object.

    Design goals:
    - Dict-compatible (tests + JSON serialization)
    - Attribute-access convenience (resp.order_id)
    - Stable string representation (logging / debugging)
    - No execution logic embedded

    This object represents the *parent* order lifecycle state,
    not individual child fills.
    """

    __slots__ = ("order_id",)

    def __init__(self, order_id: str, status: str, fill_ratio: float = 0.0):
        super().__init__()
        self["order_id"] = order_id
        self["status"] = status
        self["fill_ratio"] = float(fill_ratio)

        # Attribute mirror (tests depend on this)
        self.order_id = order_id

    def __str__(self) -> str:
        return self.order_id

    def __repr__(self) -> str:
        return f"ParentResponse({self.order_id!r}, status={self['status']!r})"
