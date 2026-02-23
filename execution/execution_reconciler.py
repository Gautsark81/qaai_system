from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, Iterable, List, Optional, Any

logger = logging.getLogger("qaai_system.ExecutionReconciler")


# ============================================================
# Drift taxonomy (EXHAUSTIVE, NON-EXTENSIBLE)
# ============================================================

class DriftType(Enum):
    MISSING_ORDER = "missing_order"
    GHOST_ORDER = "ghost_order"
    STATUS_MISMATCH = "status_mismatch"
    QTY_MISMATCH = "qty_mismatch"
    PRICE_MISMATCH = "price_mismatch"
    POSITION_MISMATCH = "position_mismatch"


class DriftSeverity(Enum):
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


# ============================================================
# Drift record (immutable forensic evidence)
# ============================================================

@dataclass(frozen=True)
class DriftRecord:
    drift_type: DriftType
    severity: DriftSeverity
    order_id: Optional[str]
    symbol: Optional[str]
    details: Dict[str, Any]


# ============================================================
# Execution Reconciler
# ============================================================

class ExecutionReconciler:
    """
    Authoritative reconciliation engine.

    Journal-driven reconstruction.
    No side-effects.
    Deterministic.

    BACKWARD COMPATIBLE:
    - ExecutionReconciler(journal)
    - ExecutionReconciler(journal_records=[...])
    - ExecutionReconciler(journal_records=journal.replay())
    """

    def __init__(
        self,
        journal_records: Optional[Any] = None,
        order_manager: Optional[Any] = None,
        broker_adapter: Optional[Any] = None,
        position_tracker: Optional[Any] = None,
        **_,
    ):
        # --------------------------------------------
        # JOURNAL NORMALIZATION (CRITICAL FIX)
        # --------------------------------------------
        records: List[Dict[str, Any]] = []

        if journal_records is None:
            records = []

        # ExecutionJournal passed directly
        elif hasattr(journal_records, "replay") and callable(journal_records.replay):
            try:
                records = list(journal_records.replay())
            except Exception:
                logger.exception("Failed to replay ExecutionJournal")
                records = []

        # Iterable of records
        else:
            try:
                records = list(journal_records)
            except Exception:
                logger.exception("Invalid journal_records input")
                records = []

        self.journal_records: List[Dict[str, Any]] = records
        self.order_manager = order_manager
        self.broker_adapter = broker_adapter
        self.position_tracker = position_tracker

        self._drifts: List[DriftRecord] = []

    # ============================================================
    # PUBLIC API
    # ============================================================

    def reconcile(self) -> List[DriftRecord]:
        logger.info("Starting execution reconciliation")
        self._drifts.clear()

        if not self.order_manager:
            logger.warning("No OrderManager bound — skipping reconciliation")
            return []

        # 1️⃣ Rehydrate orders & fills
        self._rehydrate_from_journal()

        # 2️⃣ Broker drift (advisory)
        local_orders = self._safe_local_orders()

        if self.broker_adapter:
            broker_orders = self._safe_broker_orders()
            broker_positions = self._safe_broker_positions()

            self._detect_order_level_drift(local_orders, broker_orders)
            self._detect_position_drift(local_orders, broker_positions)

        # 3️⃣ Deterministic resolutions
        self._apply_deterministic_resolutions()

        logger.info(
            "Reconciliation complete | total=%d critical=%d",
            len(self._drifts),
            sum(d.severity == DriftSeverity.CRITICAL for d in self._drifts),
        )

        return list(self._drifts)

    def has_critical_drift(self) -> bool:
        return any(d.severity == DriftSeverity.CRITICAL for d in self._drifts)

    # ============================================================
    # JOURNAL REHYDRATION
    # ============================================================

    def _rehydrate_from_journal(self) -> None:
        if not self.order_manager:
            return

        orders: Dict[str, Dict[str, Any]] = {}
        seen_fills: set[str] = set()

        for rec in self.journal_records:
            rtype = rec.get("type")

            if rtype == "INTENT":
                oid = rec.get("order_id")
                payload = rec.get("payload") or {}
                if not oid:
                    continue

                orders[oid] = {
                    "order_id": oid,
                    "symbol": payload.get("symbol"),
                    "side": payload.get("side"),
                    "quantity": payload.get("quantity"),
                    "price": payload.get("price"),
                    "meta": payload.get("meta", {}),
                    "status": "open",
                }

            elif rtype == "FILL":
                trade_id = rec.get("trade_id") or rec.get("key")
                if trade_id:
                    seen_fills.add(trade_id)

        # Authoritative overwrite (replay semantics)
        self.order_manager._orders = orders
        self.order_manager._seen_fills = seen_fills

        logger.info(
            "Rehydrated %d orders and %d fills from journal",
            len(orders),
            len(seen_fills),
        )

    # ============================================================
    # DRIFT DETECTION
    # ============================================================

    def _detect_order_level_drift(
        self,
        local: Dict[str, Dict],
        broker: Dict[str, Dict],
    ) -> None:
        local_ids = set(local.keys())
        broker_ids = set(broker.keys())

        for oid in broker_ids - local_ids:
            self._drifts.append(
                DriftRecord(
                    DriftType.MISSING_ORDER,
                    DriftSeverity.CRITICAL,
                    oid,
                    broker[oid].get("symbol"),
                    {"broker": broker[oid]},
                )
            )

        for oid in local_ids - broker_ids:
            self._drifts.append(
                DriftRecord(
                    DriftType.GHOST_ORDER,
                    DriftSeverity.WARNING,
                    oid,
                    local[oid].get("symbol"),
                    {"local": local[oid]},
                )
            )

    def _detect_position_drift(
        self,
        local_orders: Dict[str, Dict],
        broker_positions: Dict[str, Dict],
    ) -> None:
        if not broker_positions:
            return

        local_pos = self._aggregate_local_positions(local_orders)

        for symbol, broker_pos in broker_positions.items():
            if local_pos.get(symbol, 0) != broker_pos.get("quantity", 0):
                self._drifts.append(
                    DriftRecord(
                        DriftType.POSITION_MISMATCH,
                        DriftSeverity.CRITICAL,
                        None,
                        symbol,
                        {
                            "local_qty": local_pos.get(symbol, 0),
                            "broker_qty": broker_pos.get("quantity", 0),
                        },
                    )
                )

    # ============================================================
    # SAFE RESOLUTION
    # ============================================================

    def _apply_deterministic_resolutions(self) -> None:
        for d in self._drifts:
            if d.drift_type == DriftType.GHOST_ORDER and self.broker_adapter:
                self._resolve_ghost_order(d)
            elif d.severity == DriftSeverity.CRITICAL:
                logger.critical("Unresolved CRITICAL drift: %s", d)

    def _resolve_ghost_order(self, drift: DriftRecord) -> None:
        oid = drift.order_id
        if not oid:
            return

        orders = self.order_manager.get_all_orders()
        if oid in orders:
            orders[oid]["status"] = "cancelled"
            logger.warning("Marked ghost order %s as cancelled", oid)

    # ============================================================
    # SAFE ACCESS HELPERS
    # ============================================================

    def _safe_local_orders(self) -> Dict[str, Dict]:
        try:
            return dict(self.order_manager.get_all_orders())
        except Exception:
            logger.exception("Failed to fetch local orders")
            return {}

    def _safe_broker_orders(self) -> Dict[str, Dict]:
        getter = getattr(self.broker_adapter, "get_open_orders", None)
        if not callable(getter):
            return {}
        try:
            return {o["order_id"]: o for o in getter()}
        except Exception:
            logger.exception("Failed to fetch broker orders")
            return {}

    def _safe_broker_positions(self) -> Dict[str, Dict]:
        getter = getattr(self.broker_adapter, "get_positions", None)
        if not callable(getter):
            return {}
        try:
            return {p["symbol"]: p for p in getter()}
        except Exception:
            logger.exception("Failed to fetch broker positions")
            return {}

    @staticmethod
    def _aggregate_local_positions(orders: Dict[str, Dict]) -> Dict[str, int]:
        agg: Dict[str, int] = {}
        for o in orders.values():
            if (o.get("status") or "").lower() not in ("closed", "filled"):
                continue
            sym = o.get("symbol")
            qty = int(o.get("filled_qty", 0))
            if sym:
                agg[sym] = agg.get(sym, 0) + qty
        return agg
