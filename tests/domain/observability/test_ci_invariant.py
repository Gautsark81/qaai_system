from domain.observability.ci_invariant import CIInvariant


def test_ci_blocks_failures():
    assert CIInvariant.enforce(0) is True
    assert CIInvariant.enforce(1) is False
