from datetime import datetime
from modules.operator_dashboard.state_assembler import (
    DashboardStateAssembler,
)


def test_state_assembler_lifecycle():
    records = [
        {
            "strategy_id": "s1",
            "stage": "LIVE",
            "updated_at": datetime.utcnow(),
        }
    ]

    assembler = DashboardStateAssembler()
    dtos = assembler.assemble_lifecycle(records)

    assert dtos[0].strategy_id == "s1"
    assert dtos[0].stage == "LIVE"


def test_state_assembler_approvals():
    records = [
        {
            "strategy_id": "s1",
            "approved": True,
            "approver": "admin",
            "expires_at": datetime.utcnow(),
            "reason": "OK",
        }
    ]

    assembler = DashboardStateAssembler()
    dtos = assembler.assemble_approvals(records)

    assert dtos[0].approved is True
