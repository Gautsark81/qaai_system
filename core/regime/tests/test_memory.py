from core.regime.memory import RegimeMemory


def test_expected_persistence_default():
    mem = RegimeMemory()
    assert mem.expected_persistence("X") == 0.5
