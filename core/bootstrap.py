# core/bootstrap.py

from core.runtime.system_runtime import SystemRuntime
from core.execution.guards import register_kill_switch, assert_execution_allowed
from core.safety.kill_switch import KillSwitch  # your existing implementation
from core.telemetry.emitter import TelemetryEmitter  # adapt to your emitter

# create or import your global KillSwitch instance used by the process:
# If you already instantiate a KillSwitch singleton elsewhere, import it instead.
global_kill_switch = KillSwitch(telemetry=TelemetryEmitter())

# Register provider
register_kill_switch(lambda: global_kill_switch)

# Boot-time enforcement: do not start schedulers / orchestrator until enforced
assert_execution_allowed(callsite="boot/init")


def bootstrap_system(
    *,
    runner,
    run_registry,
    strategy_registry,
    strategy_health_store,
    capital_allocator,
    evidence_store,
    environment,
):
    """
    Bootstrap the governed system runtime.
    """

    return SystemRuntime(
        runner=runner,
        run_registry=run_registry,
        strategy_registry=strategy_registry,
        strategy_health_store=strategy_health_store,
        capital_allocator=capital_allocator,
        evidence_store=evidence_store,
        environment=environment,
    )
