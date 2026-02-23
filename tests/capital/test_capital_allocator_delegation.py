from core.capital.allocator import CapitalAllocator
from core.capital.result import CapitalAllocationResult
from core.capital.contracts import CapitalDecisionContext


class DummyCompositionEngine:
    def compose(self, context):
        return CapitalAllocationResult(
            strategy_id=context.strategy_id,
            allocated_capital=1000.0,
            rationale=["dummy"],
        )


def test_allocator_delegates_to_composition_engine():
    engine = DummyCompositionEngine()
    allocator = CapitalAllocator(composition_engine=engine)

    context = CapitalDecisionContext(
        strategy_id="s1",
        base_capital=5000.0,
        lifecycle_state=None,
        modifiers=[],
    )

    result = allocator.allocate(context)

    assert result.allocated_capital == 1000.0
    assert result.rationale == ["dummy"]
