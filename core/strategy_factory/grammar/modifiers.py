from dataclasses import dataclass
from typing import Literal

ModifierType = Literal[
    "EXIT:TIME",
    "EXIT:ATR",
    "EXIT:TRAILING",
    "FILTER:REGIME",
    "FILTER:LIQUIDITY",
]


@dataclass(frozen=True)
class Modifier:
    name: ModifierType
