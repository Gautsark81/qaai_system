# modules/qnme/tests/test_fusion.py
from modules.qnme.fusion import weighted_union
from modules.strategy.base import Signal

def test_weighted_union():
    s1 = Signal("s1", "FOO", "BUY", 1, score=0.5)
    s2 = Signal("s2", "FOO", "BUY", 1, score=1.5)
    out = weighted_union([[s1], [s2]], [0.6, 0.4])
    assert len(out) == 1
    assert abs(out[0].score - (0.5*0.6 + 1.5*0.4)) < 1e-6
