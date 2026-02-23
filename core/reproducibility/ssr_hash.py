# core/reproducibility/ssr_hash.py

from __future__ import annotations
from typing import Dict, Any
from .utils import sha256_json


def compute_ssr_hash(metrics: Dict[str, Any]) -> str:
    """
    metrics must include deterministic numeric outputs
    """
    return sha256_json(metrics)