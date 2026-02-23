from dataclasses import dataclass


@dataclass(frozen=True)
class AuthorizedTradeRecord:
    intent_id: str
    symbol: str
    side: str
    authorized_capital: float   # ₹
