from datetime import datetime, timezone, timedelta

import pytest

from core.governance.capital_usage.capital_usage_ledger import (
    CapitalUsageLedger,
    CapitalUsageEntry,
)
from core.governance.capital_usage.capital_exposure_reconciler import (
    CapitalExposureReconciler,
)


def test_reconciliation_latest_timestamp_wins():
    ledger = CapitalUsageLedger()
    now = datetime.now(timezone.utc)

    ledger.append(
        CapitalUsageEntry(
            strategy_id="STRAT-1",
            governance_id="gov-1",
            allocated_capital=1_000_000,
            deployed_capital=800_000,
            realized_pnl=10_000,
            timestamp=now,
        )
    )

    ledger.append(
        CapitalUsageEntry(
            strategy_id="STRAT-1",
            governance_id="gov-1",
            allocated_capital=1_000_000,
            deployed_capital=1_200_000,
            realized_pnl=20_000,
            timestamp=now + timedelta(seconds=1),
        )
    )

    reconciler = CapitalExposureReconciler()

    state = reconciler.reconcile(
        ledger=ledger,
        strategy_id="STRAT-1",
        governance_id="gov-1",
    )

    assert state.deployed_capital == 1_200_000
    assert state.over_allocated is True
    assert state.utilization_ratio == 1.2


def test_missing_entries_raises():
    ledger = CapitalUsageLedger()
    reconciler = CapitalExposureReconciler()

    with pytest.raises(ValueError):
        reconciler.reconcile(
            ledger=ledger,
            strategy_id="STRAT-1",
            governance_id="gov-1",
        )