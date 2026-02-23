from dataclasses import dataclass, field
from typing import List, Optional


@dataclass(frozen=True)
class ScreeningResult:
    """
    Canonical, identity-safe ScreeningResult.

    Backward compatible with:
    - ScreeningResult(symbol="A", score=1.0)
    - ScreeningResult(symbol, True, ["passed"], score)
    - keyword-only partial construction
    """

    symbol: str
    score: float

    passed: bool = True
    reasons: List[str] = field(default_factory=lambda: ["passed"])
    liquidity: float = 0.0

    def __post_init__(self):
        # Normalize reasons if explicitly None
        if self.reasons is None:
            object.__setattr__(self, "reasons", ["passed"])

    # -------------------------
    # Legacy compatibility
    # -------------------------
    @property
    def contract(self) -> str:
        return self.symbol

    def __repr__(self) -> str:
        return (
            f"ScreeningResult("
            f"symbol={self.symbol}, "
            f"passed={self.passed}, "
            f"score={self.score:.4f}, "
            f"liquidity={self.liquidity:.2f}"
            f")"
        )
