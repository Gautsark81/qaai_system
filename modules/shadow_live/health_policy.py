from dataclasses import dataclass


@dataclass(frozen=True)
class ShadowHealthPolicy:
    max_drawdown_pct: float      # e.g. 5%
    min_ssr: float               # e.g. 0.5
    max_loss_abs: float          # absolute INR loss


class ShadowHealthEvaluator:
    def violated(
        self,
        *,
        peak_pnl: float,
        current_pnl: float,
        ssr: float,
        policy: ShadowHealthPolicy,
    ) -> bool:

        drawdown = peak_pnl - current_pnl

        if peak_pnl > 0:
            drawdown_pct = drawdown / peak_pnl
            if drawdown_pct > policy.max_drawdown_pct:
                return True

        if ssr < policy.min_ssr:
            return True

        if abs(current_pnl) > policy.max_loss_abs and current_pnl < 0:
            return True

        return False
