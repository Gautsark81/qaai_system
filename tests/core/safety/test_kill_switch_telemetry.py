from core.safety.kill_switch import KillSwitch
from core.safety.scopes import KillScope
from core.telemetry.types import TelemetrySeverity


def test_kill_switch_emits_critical_once(telemetry_emitter, telemetry_sink):
    ks = KillSwitch(telemetry=telemetry_emitter)

    ks.trip(KillScope.GLOBAL, reason="latency breach")
    ks.trip(KillScope.GLOBAL, reason="duplicate")  # no second emit

    critical = [
        e for e in telemetry_sink.events
        if e.severity == TelemetrySeverity.CRITICAL
    ]

    assert len(critical) == 1
