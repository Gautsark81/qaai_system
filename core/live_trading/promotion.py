from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from core.strategy_factory.registry import StrategyRegistry
from core.live_trading.status import ExecutionStatus
from core.live_trading.audit import AuditEvent
from core.live_trading.alerts import OperatorAlert


# ============================
# Canary Policy
# ============================

@dataclass(frozen=True)
class CanaryPolicy:
    """
    Hard, non-negotiable thresholds for canary governance.

    Canary is about capital protection, not performance.
    """
    max_divergence: float
    max_slippage: float


# ============================
# Canary Promotion Engine
# ============================

class CanaryPromotionEngine:
    """
    Canary governance engine.

    GUARANTEES:
    - NEVER mutates strategy lifecycle (LIVE / PAPER / BACKTESTED)
    - ONLY controls execution permission
    - Fully deterministic
    - Side effects are OPTIONAL and injected
    - Safe to run per-bar / per-trade

    This engine is the FINAL safety net before capital damage.
    """

    def __init__(
        self,
        *,
        registry: StrategyRegistry,
        policy: CanaryPolicy,
        audit_log: Optional[object] = None,
        alerts: Optional[list] = None,
    ):
        self.registry = registry
        self.policy = policy
        self.audit_log = audit_log
        self.alerts = alerts

    # ============================
    # Core Evaluation
    # ============================

    def evaluate(
        self,
        *,
        dna: str,
        divergence_score: float,
        avg_slippage: float,
    ) -> str:
        """
        Evaluate canary health for a LIVE strategy.

        Returns
        -------
        str:
            CONTINUE | FREEZE | DOWNGRADE
        """

        record = self.registry.get(dna)

        # Ensure execution_status exists (non-invasive)
        if not hasattr(record, "execution_status"):
            record.execution_status = ExecutionStatus.ACTIVE

        # ---------- RULE 1: DIVERGENCE ----------
        if divergence_score > self.policy.max_divergence:
            self._freeze(
                record=record,
                decision="DOWNGRADE",
                reason="DIVERGENCE",
                metrics={
                    "divergence": divergence_score,
                    "threshold": self.policy.max_divergence,
                },
            )
            return "DOWNGRADE"

        # ---------- RULE 2: SLIPPAGE ----------
        if abs(avg_slippage) > self.policy.max_slippage:
            self._freeze(
                record=record,
                decision="FREEZE",
                reason="SLIPPAGE",
                metrics={
                    "slippage": avg_slippage,
                    "threshold": self.policy.max_slippage,
                },
            )
            return "FREEZE"

        # ---------- HEALTHY ----------
        record.execution_status = ExecutionStatus.ACTIVE
        return "CONTINUE"

    # ============================
    # Internal Helpers
    # ============================

    def _freeze(
        self,
        *,
        record,
        decision: str,
        reason: str,
        metrics: dict,
    ) -> None:
        """
        Freeze execution and emit optional side effects.

        NOTE:
        - Lifecycle is NOT modified
        - Only execution permission is controlled
        """

        record.execution_status = ExecutionStatus.FROZEN
        now = datetime.utcnow()

        # ---- AUDIT LOG (STRICT, IMMUTABLE) ----
        if self.audit_log is not None:
            self.audit_log.append(
                AuditEvent(
                    timestamp=now,
                    dna=record.dna,
                    event_type=f"CANARY_{decision}",
                    payload={
                        "reason": reason,
                        **metrics,
                    },
                )
            )

        # ---- OPERATOR ALERT (HUMAN-FACING) ----
        if self.alerts is not None:
            self.alerts.append(
                OperatorAlert(
                    timestamp=now,
                    level="CRITICAL" if decision == "DOWNGRADE" else "WARNING",
                    message=(
                        f"Canary {decision}: strategy={record.dna}, "
                        f"reason={reason}, metrics={metrics}"
                    ),
                )
            )
