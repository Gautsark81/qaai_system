from core.strategy_factory.registry import StrategyRegistry
from core.live_trading.status import ExecutionStatus


def get_canary_overrides():
    registry = StrategyRegistry.global_instance()

    overrides = {}

    for dna, record in registry.all().items():
        status = getattr(record, "execution_status", None)
        if status and status != ExecutionStatus.ACTIVE:
            overrides[dna] = {
                "execution_status": status,
                "decision": status.name,
                "last_event": getattr(record, "last_audit_event", None),
            }

    return overrides
