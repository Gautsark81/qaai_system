from dataclasses import dataclass
from typing import Dict, Iterable, Mapping


@dataclass(frozen=True)
class PortfolioCapInput:
    """
    Input after allocation, before execution.

    allocations:
        strategy_id -> allocated capital
    symbols:
        strategy_id -> symbol
    prices:
        strategy_id -> execution price
    """
    allocations: Dict[str, float]
    symbols: Dict[str, str]
    prices: Dict[str, float]


@dataclass(frozen=True)
class PortfolioCapResult:
    capped_allocations: Dict[str, float]
    total_allocated: float
    dropped: Iterable[str]


class PortfolioCaps:
    """
    Enforces portfolio-level capital and exposure caps.

    This class NEVER increases allocation.
    """

    def __init__(
        self,
        *,
        max_per_strategy: float | None = None,
        max_per_symbol: float | None = None,
        max_total_exposure: float | None = None,
    ):
        self._max_per_strategy = max_per_strategy
        self._max_per_symbol = max_per_symbol
        self._max_total_exposure = max_total_exposure

    def apply(self, inp: PortfolioCapInput) -> PortfolioCapResult:
        allocations = dict(inp.allocations)
        dropped: set[str] = set()

        # ---------- Per-strategy cap ----------
        if self._max_per_strategy is not None:
            for sid, value in allocations.items():
                if value > self._max_per_strategy:
                    allocations[sid] = self._max_per_strategy

        # ---------- Per-symbol cap ----------
        if self._max_per_symbol is not None:
            by_symbol: Dict[str, Dict[str, float]] = {}
            for sid, value in allocations.items():
                sym = inp.symbols.get(sid)
                if sym is None:
                    allocations[sid] = 0.0
                    dropped.add(sid)
                    continue
                by_symbol.setdefault(sym, {})[sid] = value

            for sym, bucket in by_symbol.items():
                total = sum(bucket.values())
                if total <= self._max_per_symbol:
                    continue

                scale = self._max_per_symbol / total if total > 0 else 0.0
                for sid in bucket:
                    allocations[sid] *= scale

        # ---------- Global exposure cap ----------
        if self._max_total_exposure is not None:
            total = sum(allocations.values())
            if total > self._max_total_exposure:
                scale = self._max_total_exposure / total if total > 0 else 0.0
                for sid in allocations:
                    allocations[sid] *= scale

        # ---------- Clean negatives ----------
        for sid, value in list(allocations.items()):
            if value <= 0:
                allocations[sid] = 0.0
                dropped.add(sid)

        total_allocated = sum(allocations.values())

        return PortfolioCapResult(
            capped_allocations=allocations,
            total_allocated=total_allocated,
            dropped=tuple(sorted(dropped)),
        )
