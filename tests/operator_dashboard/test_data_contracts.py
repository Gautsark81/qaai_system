from datetime import datetime
from modules.operator_dashboard.data_contracts import (
    StrategyLifecycleDTO,
    ApprovalStatusDTO,
)


def test_strategy_lifecycle_dto():
    dto = StrategyLifecycleDTO(
        strategy_id="s1",
        stage="LIVE",
        updated_at=datetime.utcnow(),
    )
    assert dto.stage == "LIVE"


def test_approval_status_dto():
    dto = ApprovalStatusDTO(
        strategy_id="s1",
        approved=True,
        approver="admin",
        expires_at=datetime.utcnow(),
        reason="Stable SSR",
    )
    assert dto.approved is True
