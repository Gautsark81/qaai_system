# modules/operator_dashboard/tests/test_alerts.py

from operator_dashboard.state_assembler import DashboardStateAssembler

def test_alerts_are_safe():
    alerts = DashboardStateAssembler().assemble().alerts

    for a in alerts:
        assert a.alert_type
        assert a.severity
        assert a.message
