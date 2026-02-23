from __future__ import annotations

from dataclasses import dataclass
from typing import Protocol

from strategies.base import StrategySignal
from risk.base import RiskContextProtocol, RiskDecision


class RiskRule(Protocol):
    name: str

    def evaluate(
        self,
        ctx: RiskContextProtocol,
        signal: StrategySignal,
    ) -> RiskDecision:
        ...


@dataclass(slots=True)
class MaxSymbolExposureRule:
    name: str = "max_symbol_exposure"
    max_notional_per_symbol: float = 0.0  # 0 => disabled

    def evaluate(
        self,
        ctx: RiskContextProtocol,
        signal: StrategySignal,
    ) -> RiskDecision:
        if self.max_notional_per_symbol <= 0:
            return RiskDecision(True, "DISABLED", signal.size)

        current = ctx.symbol_exposure(signal.symbol)
        # assume size maps 1:1 to notional unit for now; plug real px later
        new_exposure = current + signal.size

        if new_exposure <= self.max_notional_per_symbol:
            return RiskDecision(True, "OK", signal.size, {"symbol_exposure": new_exposure})

        # shrink size
        allowed_size = max(0.0, self.max_notional_per_symbol - current)
        if allowed_size <= 0:
            return RiskDecision(False, "SYMBOL_LIMIT_REACHED", 0.0, {"symbol_exposure": current})

        return RiskDecision(True, "REDUCED_TO_LIMIT", allowed_size, {"symbol_exposure": current + allowed_size})


@dataclass(slots=True)
class VolatilitySizerRule:
    name: str = "volatility_sizer"
    target_risk_unit: float = 1.0  # custom scalar

    def evaluate(
        self,
        ctx: RiskContextProtocol,
        signal: StrategySignal,
    ) -> RiskDecision:
        vol = ctx.symbol_volatility(signal.symbol)
        if vol <= 0:
            return RiskDecision(True, "NO_VOL_DATA", signal.size, {"vol": 0.0})
        # naive inverse-vol adjustment
        adjusted = min(signal.size, self.target_risk_unit / vol)
        return RiskDecision(True, "OK", adjusted, {"vol": vol})
