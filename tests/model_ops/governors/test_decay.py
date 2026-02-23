from qaai_system.model_ops.governors import HardKillDecay, LinearDecay


def test_hard_kill_decay_sets_zero():
    decay = HardKillDecay()
    assert decay.next_weight(0.7) == 0.0


def test_linear_decay_reduces_weight():
    decay = LinearDecay(step=0.2)
    assert decay.next_weight(0.7) == 0.5


def test_linear_decay_never_negative():
    decay = LinearDecay(step=0.5)
    assert decay.next_weight(0.3) == 0.0
