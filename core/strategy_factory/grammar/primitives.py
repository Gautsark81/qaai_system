from dataclasses import dataclass
from typing import Optional

@dataclass
class Primitive:
    name: str
    param: Optional[int] = None

    @property
    def window(self) -> Optional[int]:
        return self.param

    def mutate_window(self, delta: int) -> "Primitive":
        if self.param is None:
            return self
        return Primitive(self.name, max(1, self.param + delta))

    def __str__(self) -> str:
        return f"{self.name}({self.param})" if self.param else self.name


PRIMITIVES = {
    "price",
    "volume",
    "returns",
    "volatility",
    "Momentum",
    "momentum",
}

def is_valid_primitive(value) -> bool:
    if isinstance(value, Primitive):
        return value.name in PRIMITIVES
    if isinstance(value, str):
        return value in PRIMITIVES
    return False
