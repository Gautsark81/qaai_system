from datetime import datetime
from typing import Optional

from core.evidence.drift_gap.models import (
    DriftGapRecord,
    DriftGapType,
    DriftSeverity,
)


class DriftGapDetector:
    def detect(
        self,
        expected_state: dict,
        observed_state: dict,
        as_of: datetime,
    ) -> Optional[DriftGapRecord]:

        # POSITION DRIFT
        for symbol, expected_qty in expected_state.get("position", {}).items():
            observed_qty = observed_state.get("position", {}).get(symbol, 0)
            if expected_qty != observed_qty:
                return DriftGapRecord(
                    gap_type=DriftGapType.POSITION,
                    severity=DriftSeverity.WARN,
                    detected_at=as_of,
                    details={
                        "symbol": symbol,
                        "expected": expected_qty,
                        "observed": observed_qty,
                    },
                )

        # CAPITAL DRIFT
        if expected_state.get("capital_used") != observed_state.get("capital_used"):
            return DriftGapRecord(
                gap_type=DriftGapType.CAPITAL,
                severity=DriftSeverity.WARN,
                detected_at=as_of,
                details={
                    "expected": expected_state.get("capital_used"),
                    "observed": observed_state.get("capital_used"),
                },
            )

        # ORDER STATE DRIFT
        for oid, expected_status in expected_state.get("orders", {}).items():
            observed_status = observed_state.get("orders", {}).get(oid)
            if expected_status != observed_status:
                return DriftGapRecord(
                    gap_type=DriftGapType.ORDER_STATE,
                    severity=DriftSeverity.INFO,
                    detected_at=as_of,
                    details={
                        "order_id": oid,
                        "expected": expected_status,
                        "observed": observed_status,
                    },
                )

        return None
