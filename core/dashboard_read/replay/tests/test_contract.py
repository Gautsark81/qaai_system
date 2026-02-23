from core.dashboard_read.replay.contract import ReplayContract, ReplayEngine
from core.dashboard_read.snapshot import SystemSnapshot
from core.dashboard_read.replay.result import ReplayResult


def test_replay_contract_defaults_are_strict():
    contract = ReplayContract()

    assert contract.requires_sealed_snapshot is True
    assert contract.providers_allowed is False
    assert contract.side_effects_allowed is False
    assert contract.wall_clock_allowed is False
    assert contract.randomness_allowed is False
    assert contract.network_allowed is False


def test_replay_engine_is_abstract():
    class Dummy(ReplayEngine):
        pass

    try:
        Dummy()  # pragma: no cover
        assert False, "Abstract replay engine should not be instantiable"
    except TypeError:
        assert True