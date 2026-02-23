"""
Compatibility bridge for legacy imports.

Real implementation lives in:
core.governance.capital_usage.capital_throttle_ledger
"""

from core.governance.capital_usage.capital_throttle_ledger import (
    CapitalThrottleLedger,
    CapitalThrottleLedgerEntry,
)

__all__ = [
    "CapitalThrottleLedger",
    "CapitalThrottleLedgerEntry",
]