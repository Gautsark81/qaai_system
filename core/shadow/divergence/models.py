from dataclasses import dataclass


@dataclass(frozen=True)
class SignalSnapshot:
    symbol: str
    side: str
    quantity: int
    price: float


@dataclass(frozen=True)
class FillSnapshot:
    symbol: str
    side: str
    quantity: int
    avg_price: float


@dataclass(frozen=True)
class CapitalExpectation:
    expected_capital: float


@dataclass(frozen=True)
class CapitalReality:
    actual_capital: float
