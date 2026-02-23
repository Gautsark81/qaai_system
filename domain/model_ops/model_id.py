from dataclasses import dataclass


@dataclass(frozen=True)
class ModelID:
    name: str
    version: str        # e.g. 1.2.0
    hash: str           # artifact hash
