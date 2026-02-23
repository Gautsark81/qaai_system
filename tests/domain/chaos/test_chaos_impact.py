from domain.chaos.chaos_impact import ChaosImpact


def test_chaos_impact():
    i = ChaosImpact(True, "CRITICAL")
    assert i.should_halt_trading is True
