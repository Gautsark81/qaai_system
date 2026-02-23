from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class FeatureVector:
    """
    Immutable feature contract for meta-model.
    """
    values: Dict[str, float]
    window_id: str
    schema_version: str = "1.0"
