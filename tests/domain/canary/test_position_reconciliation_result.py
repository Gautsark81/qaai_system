from domain.canary.position_reconciliation_result import (
    PositionReconciliationResult
)


def test_position_reconciliation_result():
    r = PositionReconciliationResult("NIFTY", 2, 3, 1, False)
    assert r.delta_qty == 1
