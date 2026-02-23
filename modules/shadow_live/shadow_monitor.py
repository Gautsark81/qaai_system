from modules.shadow_live.health_policy import (
    ShadowHealthEvaluator,
    ShadowHealthPolicy,
)
from modules.shadow_live.shadow_state import ShadowLiveState


class ShadowLiveMonitor:
    def __init__(self, policy: ShadowHealthPolicy):
        self.policy = policy
        self.evaluator = ShadowHealthEvaluator()

    def should_kill(
        self,
        state: ShadowLiveState,
        ssr: float,
    ) -> bool:
        return self.evaluator.violated(
            peak_pnl=state.peak_pnl,
            current_pnl=state.current_pnl,
            ssr=ssr,
            policy=self.policy,
        )
