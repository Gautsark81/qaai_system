import importlib
import sys
from types import ModuleType


# ---------------------------------------------------------------------
# PHASE 9 CORE MODULES (LOCKED SURFACE)
# ---------------------------------------------------------------------

PHASE_9_MODULES = [
    # Strategy contract
    "modules.strategies.base",

    # Strategy lifecycle (pure)
    "modules.strategy_lifecycle.states",
    "modules.strategy_lifecycle.store",
    "modules.strategy_lifecycle.evaluator",
    "modules.strategy_lifecycle.orchestrator",
    "modules.strategy_lifecycle.scheduler",

    # Execution (minimal, deterministic)
    "modules.execution.orchestrator",
]


FORBIDDEN_PREFIXES = (
    "modules.infra",
    "infra",
)


def _get_loaded_modules() -> set[str]:
    return {
        name
        for name, module in sys.modules.items()
        if isinstance(module, ModuleType)
    }


def test_phase_9_modules_do_not_import_infra():
    """
    Phase 9 invariant:

    Core modules MUST NOT import infra, schedulers,
    job registries, or runtime wiring.

    This test intentionally inspects sys.modules
    AFTER import to catch transitive leaks.
    """
    before = _get_loaded_modules()

    # Import all Phase 9 modules
    for module_name in PHASE_9_MODULES:
        importlib.import_module(module_name)

    after = _get_loaded_modules()
    newly_loaded = after - before

    infra_leaks = [
        m for m in newly_loaded
        if m.startswith(FORBIDDEN_PREFIXES)
    ]

    assert not infra_leaks, (
        "Phase 9 INFRA LEAK DETECTED:\n"
        f"{infra_leaks}\n\n"
        "Phase 9 core must remain pure.\n"
        "Infra wiring belongs to Phase 10+."
    )
