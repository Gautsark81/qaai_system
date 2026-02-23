from domain.canary.reconciliation_result import ReconciliationResult


def test_reconciliation_result_delta():
    r = ReconciliationResult("I1", 1000, 1020, 20, False)
    assert r.delta == 20
