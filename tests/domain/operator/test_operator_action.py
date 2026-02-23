from datetime import datetime
from domain.operator.operator_action import OperatorAction


def test_operator_action_fields():
    a = OperatorAction(
        operator_id="admin",
        action="KILL",
        target="SYSTEM",
        reason="Unexpected drift",
        timestamp=datetime.utcnow(),
    )
    assert a.action == "KILL"
