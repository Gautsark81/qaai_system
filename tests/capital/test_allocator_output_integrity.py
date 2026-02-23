from core.capital.allocator import CapitalAllocator
from core.capital.result import CapitalAllocationResult
from core.capital.contracts import CapitalDecisionContext


class SpyCompositionEngine:
    def __init__(self):
        self.called = False

    def compose(self, context):
        self.called = True
        return CapitalAllocationResult(
            strategy_id=context.strategy_id,
            allocated_capital=4200.0,
            rationale=["spy-engine"],
        )


def test_allocator_returns_exact_engine_output():
    engine = SpyCompositionEngine()
    allocator = CapitalAllocator(composition_engine=engine)

    context = CapitalDecisionContext(
        strategy_id="spy",
        base_capital=10000.0,
        lifecycle_state=None,
        modifiers=[],
    )

    result = allocator.allocate(context)

    assert engine.called is True
    assert result.allocated_capital == 4200.0
    assert result.rationale == ["spy-engine"]
