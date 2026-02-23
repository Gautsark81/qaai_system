from dataclasses import dataclass
from typing import List, Optional
from typing import Any

@dataclass(frozen=True)
class StrategyLifecycleView:
    strategy_id: str
    version: str

    lifecycle_stage: str        # generated / backtested / paper / live / canary / halted
    status: str                 # allowed / blocked / pending_approval

    backtest_ssr: Optional[float]
    paper_ssr: Optional[float]

    last_decision: Optional[str]
    last_decision_reason: Optional[str]

    human_approval_stage: Optional[str]   # paper / live / scale
    human_approval_status: Optional[str]  # approved / rejected / pending

    risk_flags: List[str]
    kill_switch_active: bool


    # ------------------------------------------------------------------
    # Backward Compatibility Layer (DO NOT REMOVE)
    # ------------------------------------------------------------------

    @property
    def execution_status(self) -> str:
        """
        Compatibility shim for legacy dashboard tests.
        Maps lifecycle_stage into execution-style status.
        """
        stage = (self.lifecycle_stage or "").lower()

        if stage in {"live", "canary"}:
            return "ACTIVE"
        if stage in {"halted"}:
            return "HALTED"
        return "INACTIVE"

    @property
    def approval(self) -> Optional[str]:
        """
        Compatibility shim for legacy governance snapshot tests.
        Combines human approval stage + status into a single string.
        """
        if self.human_approval_stage and self.human_approval_status:
            return f"{self.human_approval_stage}:{self.human_approval_status}"
        return None

    # Alias for legacy naming
    @property
    def StrategySnapshot(self) -> Any:
        """
        Legacy compatibility placeholder.
        Some old tests reference StrategySnapshot type.
        This ensures object still resolves attribute lookups safely.
        """
        return self
