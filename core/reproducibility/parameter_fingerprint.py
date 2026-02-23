# core/reproducibility/parameter_fingerprint.py

from __future__ import annotations
from typing import Dict, Any

from .utils import sha256_json


def compute_parameter_hash(parameter_config: Dict[str, Any]) -> str:
    return sha256_json(parameter_config)