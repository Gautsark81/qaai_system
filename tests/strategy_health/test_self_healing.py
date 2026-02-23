from modules.strategy_health.self_healing_orchestrator import (
    SelfHealingOrchestrator,
)
from modules.strategy_health.decay_detector import DecaySignal
from modules.strategy_health.state_machine import StrategyState
from modules.strategy_health.telemetry import StrategyTelemetry


def test_healing_rejected_if_not_paused():
    orch = SelfHealingOrchestrator()

    result = orch.heal(
        strategy_id="s1",
        state=StrategyState.ACTIVE,
        decay_signal=DecaySignal(
            level="STRUCTURAL_DECAY",
            reasons=["test"],
            windows_confirmed=[30, 60],
        ),
        telemetry=StrategyTelemetry(strategy_id="s1"),
    )

    assert not result.success


def test_healing_rejected_if_decay_not_structural():
    orch = SelfHealingOrchestrator()

    result = orch.heal(
        strategy_id="s1",
        state=StrategyState.PAUSED,
        decay_signal=DecaySignal(
            level="SOFT_DECAY",
            reasons=["test"],
            windows_confirmed=[30],
        ),
        telemetry=StrategyTelemetry(strategy_id="s1"),
    )

    assert not result.success


def test_healing_generates_new_strategy_id():
    orch = SelfHealingOrchestrator()

    result = orch.heal(
        strategy_id="s1",
        state=StrategyState.PAUSED,
        decay_signal=DecaySignal(
            level="STRUCTURAL_DECAY",
            reasons=["health", "drawdown"],
            windows_confirmed=[30, 60],
        ),
        telemetry=StrategyTelemetry(strategy_id="s1"),
    )

    assert result.success
    assert result.new_strategy_id is not None
    assert result.new_strategy_id.startswith("s1_heal_")
