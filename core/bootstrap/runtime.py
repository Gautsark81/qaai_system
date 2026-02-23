# core/bootstrap/runtime.py

from core.regime.engine import RegimeEngine
from core.runtime.deterministic_runner import DeterministicRunner

from core.runtime.environment import RuntimeEnvironment

from core.strategy.strategy_registry import StrategyRegistry
from core.strategy_health.aggregator import StrategyHealthAggregator

from core.capital.allocator import (
    PortfolioCapitalAllocator,
    CapitalAllocator,
)

from core.evidence.decision_store import InMemoryDecisionStore
from core.runtime.deterministic_context import DeterministicContext
from core.runtime.run_registry import RunRegistry


def build_system_runtime(*, environment: RuntimeEnvironment):
    """
    Build a governed SystemRuntime.

    Design guarantees:
    - No circular imports
    - Deterministic
    - Phase-20 red-team compatible
    """

    # -------------------------------------------------
    # Core engines (authoritative owners)
    # -------------------------------------------------

    strategy_registry = StrategyRegistry()
    strategy_health_store = StrategyHealthAggregator()

    portfolio_engine = PortfolioCapitalAllocator()
    capital_allocator = CapitalAllocator(portfolio_engine)

    evidence_store = InMemoryDecisionStore()

    # -------------------------------------------------
    # Run registry (explicit wiring)
    # -------------------------------------------------

    run_registry = RunRegistry(
        strategy_registry=strategy_registry,
        strategy_health_store=strategy_health_store,
        capital_allocator=capital_allocator,
        evidence_store=evidence_store,
    )

    # -------------------------------------------------
    # Deterministic execution context
    # -------------------------------------------------

    regime_engine = RegimeEngine(evidence_store=evidence_store)
    runner = DeterministicRunner(regime_engine=regime_engine)


    # -------------------------------------------------
    # 🔑 DELAYED IMPORT (BREAKS CIRCULAR DEPENDENCY)
    # -------------------------------------------------

    from core.runtime.system_runtime import SystemRuntime

    return SystemRuntime(
        runner=runner,
        run_registry=run_registry,
        strategy_registry=strategy_registry,
        strategy_health_store=strategy_health_store,
        capital_allocator=capital_allocator,
        evidence_store=evidence_store,
        environment=environment,
    )
