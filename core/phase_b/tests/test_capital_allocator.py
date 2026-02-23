from core.phase_b.capital_allocator import CapitalAllocator


def test_high_confidence_full_scale():
    allocator = CapitalAllocator()

    decision = allocator.decide(
        dna="x",
        confidence=0.9,
        ssr=0.7,
    )

    assert decision.scale == 1.0
    assert "high_confidence" in decision.reason


def test_low_confidence_reduced_scale():
    allocator = CapitalAllocator()

    decision = allocator.decide(
        dna="x",
        confidence=0.4,
        ssr=None,
    )

    assert decision.scale < 0.5
    assert "low_confidence" in decision.reason


def test_low_ssr_penalizes_scale():
    allocator = CapitalAllocator()

    decision = allocator.decide(
        dna="x",
        confidence=0.8,
        ssr=0.2,
    )

    assert decision.scale < 1.0
    assert "low_ssr" in decision.reason
