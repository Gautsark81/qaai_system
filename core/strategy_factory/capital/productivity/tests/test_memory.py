from core.strategy_factory.capital.productivity.memory import (
    ProductivityMemory,
    ProductivityMemoryConfig,
)


def test_memory_requires_persistence():

    memory = ProductivityMemory(
        ProductivityMemoryConfig(window_size=5, persistence_threshold=3)
    )

    rotation_map = {"A": 0.8}

    # First two cycles → no reduction
    r1 = memory.update(rotation_map)
    r2 = memory.update(rotation_map)

    assert r1["A"] == 1.0
    assert r2["A"] == 1.0

    # Third cycle → reduction applied
    r3 = memory.update(rotation_map)
    assert r3["A"] < 1.0


def test_memory_stable_when_no_underperformance():

    memory = ProductivityMemory()

    rotation_map = {"A": 1.0}

    for _ in range(5):
        result = memory.update(rotation_map)
        assert result["A"] == 1.0