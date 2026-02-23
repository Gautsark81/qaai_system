from dataclasses import dataclass


@dataclass(frozen=True)
class CapitalCompositionResult:
    requested: float
    lifecycle_adjusted: float
    final: float


class CapitalCompositionEngine:
    """
    Deterministic capital composition engine.

    Combines independent capital constraints.
    Does NOT compute risk, lifecycle, or account state.
    """

    @staticmethod
    def compose(
        *,
        requested_capital: float,
        risk_allowed_capital: float,
        lifecycle_multiplier: float,
        strategy_cap: float,
        account_available_capital: float,
    ) -> CapitalCompositionResult:

        inputs = [
            requested_capital,
            risk_allowed_capital,
            lifecycle_multiplier,
            strategy_cap,
            account_available_capital,
        ]

        # Fail closed
        if any(v is None or v <= 0 for v in inputs):
            return CapitalCompositionResult(
                requested=requested_capital or 0.0,
                lifecycle_adjusted=0.0,
                final=0.0,
            )

        if lifecycle_multiplier > 1.0:
            raise ValueError("Lifecycle multiplier must not exceed 1.0")

        lifecycle_adjusted = requested_capital * lifecycle_multiplier

        final_capital = min(
            lifecycle_adjusted,
            risk_allowed_capital,
            strategy_cap,
            account_available_capital,
        )

        return CapitalCompositionResult(
            requested=requested_capital,
            lifecycle_adjusted=lifecycle_adjusted,
            final=max(0.0, final_capital),
        )
