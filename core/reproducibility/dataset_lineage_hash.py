# core/reproducibility/dataset_lineage_hash.py

from __future__ import annotations
import hashlib
from core.reproducibility.dataset_provenance import DatasetProvenance


class DatasetLineageHasher:
    """
    Deterministic SHA256 over canonical dataset provenance.
    """

    @staticmethod
    def hash(provenance: DatasetProvenance) -> str:
        canonical_json = provenance.to_canonical_json()
        return hashlib.sha256(canonical_json.encode("utf-8")).hexdigest()