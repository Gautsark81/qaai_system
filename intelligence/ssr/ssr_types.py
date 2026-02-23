from dataclasses import dataclass


@dataclass(frozen=True)
class TradeOutcome:
    net_r: float

    @property
    def is_success(self) -> bool:
        return self.net_r > 0
