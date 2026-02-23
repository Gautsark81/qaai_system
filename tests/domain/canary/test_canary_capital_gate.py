from domain.canary.canary_capital_gate import CanaryCapitalGate
from domain.canary.canary_envelope import CanaryEnvelope


def test_canary_gate_blocks_out_of_bounds():
    env = CanaryEnvelope(10, 4000)
    assert CanaryCapitalGate.allow(env, 100) == 100
    assert CanaryCapitalGate.allow(env, 5000) is None
