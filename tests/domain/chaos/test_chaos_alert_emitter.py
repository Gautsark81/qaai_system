from domain.chaos.chaos_alert_emitter import ChaosAlertEmitter
from domain.chaos.chaos_impact import ChaosImpact
from domain.observability.alert_manager import AlertManager


def test_chaos_alert_emitted():
    mgr = AlertManager()
    impact = ChaosImpact(True, "CRITICAL")

    ChaosAlertEmitter.emit(impact, "CHAOS", mgr)
    assert len(mgr.active()) == 1
