from core.governance.reconstruction.governance_chain_reconstructor import (
    GovernanceChainReconstructor,
)


class DummyEvent:
    def __init__(self, governance_chain_id):
        self.governance_chain_id = governance_chain_id


def test_reconstruction_valid_chain():

    recon = GovernanceChainReconstructor()

    throttle = [DummyEvent("CHAIN-1")]
    scaling = [DummyEvent("CHAIN-1")]
    promotion = []

    result = recon.reconstruct(
        throttle_events=throttle,
        scaling_events=scaling,
        promotion_events=promotion,
    )

    assert result.valid
    assert len(result.chains) == 1
    assert result.chains[0].governance_chain_id == "CHAIN-1"


def test_reconstruction_detects_orphan():

    recon = GovernanceChainReconstructor()

    throttle = [DummyEvent(None)]
    scaling = []
    promotion = []

    result = recon.reconstruct(
        throttle_events=throttle,
        scaling_events=scaling,
        promotion_events=promotion,
    )

    assert not result.valid
    assert len(result.orphan_events) == 1


def test_reconstruction_detects_missing_throttle():

    recon = GovernanceChainReconstructor()

    throttle = []
    scaling = [DummyEvent("CHAIN-X")]
    promotion = []

    result = recon.reconstruct(
        throttle_events=throttle,
        scaling_events=scaling,
        promotion_events=promotion,
    )

    assert not result.valid
    assert "missing throttle event" in result.errors[0]