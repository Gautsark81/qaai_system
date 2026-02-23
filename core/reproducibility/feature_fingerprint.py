# core/reproducibility/feature_fingerprint.py

from __future__ import annotations
from typing import Dict, Any

from .utils import sha256_json


def compute_feature_hash(feature_config: Dict[str, Any]) -> str:
    return sha256_json(feature_config)