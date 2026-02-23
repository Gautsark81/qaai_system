from datetime import datetime
from domain.operator.operator_ui_state import OperatorUIState
from domain.observability.system_health import SystemHealthSnapshot


def test_operator_ui_state():
    state = OperatorUIState(
        system_health=SystemHealthSnapshot(
            timestamp=datetime.utcnow(),
            components={"execution": "OK"},
            warnings=0,
            errors=0,
        ),
        active_alerts=[],
    )
    assert state.system_health.errors == 0
