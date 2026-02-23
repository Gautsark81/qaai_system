# modules/metrics/types.py

from dataclasses import dataclass
from typing import Mapping


@dataclass(frozen=True)
class MetricSample:
    name: str
    value: float
    labels: Mapping[str, str]
