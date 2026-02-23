from core.capital_governance.concentration import build_concentration_warnings
from core.capital.allocation_report import CapitalAllocationReport
from core.capital.allocation_report import (
    AllocationReport,
    StrategyAllocation,
)


def test_concentration_warning_emitted():
    report = AllocationReport(
        strategy_allocations={
            "s1": StrategyAllocation("s1", 80.0),
            "s2": StrategyAllocation("s2", 20.0),
        }
    )

    warnings = build_concentration_warnings(report, threshold=0.7)

    assert "s1" in warnings
