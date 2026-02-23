# clients/order_reconciler.py
from __future__ import annotations
import threading
import time
import logging
from typing import Optional, Dict, Any, Iterable
from clients import metrics as metrics_module

logger = logging.getLogger(__name__)


class OrderReconciler:
    def __init__(self, order_manager, poll_interval: float = 5.0, lookback_seconds: int = 3600, idempotency_store=None):
        self.om = order_manager
        self.poll_interval = float(poll_interval)
        self.lookback_seconds = int(lookback_seconds)
        self.idempotency_store = idempotency_store
        self._stop = threading.Event()
        self._thread: Optional[threading.Thread] = None

    def start(self):
        if self._thread and self._thread.is_alive():
            return
        self._stop.clear()
        t = threading.Thread(target=self._run, name="order-reconciler", daemon=True)
        t.start()
        self._thread = t
        logger.info("OrderReconciler started")

    def stop(self):
        if self._thread:
            self._stop.set()
            self._thread.join(timeout=3.0)
            self._thread = None
            logger.info("OrderReconciler stopped")

    def _iter_candidates(self) -> Iterable[Dict[str, Any]]:
        now = time.time()
        local = self.om.list_local_orders()
        for oid, meta in local.items():
            created_at = meta.get("created_at", 0)
            if now - float(created_at) > self.lookback_seconds:
                continue
            status = meta.get("status", "").upper()
            if status in ("FILLED", "CANCELLED", "REJECTED", "EXPIRED"):
                continue
            yield meta

    def _reconcile_one(self, meta: Dict[str, Any]) -> None:
        oid = meta.get("order_id")
        try:
            newmeta = self.om.get_order_status(oid)
            logger.debug("Reconciled %s -> %s", oid, newmeta.get("status"))
            if self.idempotency_store and meta.get("idempotency_key"):
                try:
                    self.idempotency_store[meta["idempotency_key"]] = newmeta
                except Exception:
                    logger.exception("Failed to persist idempotency for %s", meta.get("idempotency_key"))
            try:
                if metrics_module is not None and hasattr(metrics_module, "reconciler_runs"):
                    metrics_module.reconciler_runs.inc()
            except Exception:
                pass
        except Exception:
            logger.exception("Failed to reconcile order %s", oid)

    def _run(self):
        logger.debug("OrderReconciler thread running")
        while not self._stop.is_set():
            try:
                for meta in list(self._iter_candidates()):
                    self._reconcile_one(meta)
            except Exception:
                logger.exception("Error during reconciliation cycle")
            self._stop.wait(self.poll_interval)
        logger.debug("OrderReconciler thread exiting")

    def run_once(self, timeout: Optional[float] = None) -> None:
        """
        Run a single reconciliation pass synchronously. Useful at startup to ensure order cache
        is reconciled before accepting new orders or starting other subsystems.
        timeout: not used for now but kept for compatible signature.
        """
        logger.info("OrderReconciler running single reconciliation pass")
        try:
            for meta in list(self._iter_candidates()):
                self._reconcile_one(meta)
        except Exception:
            logger.exception("Error during single reconciliation pass")
