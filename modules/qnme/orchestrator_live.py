# modules/qnme/orchestrator_live.py
"""
Live-capable orchestrator that integrates with:
- modules.dhan.ws_provider.WsProvider (or similar)
- OrderManager (modules.order.manager.OrderManager) for execution

Safety: default runs in shadow mode. To enable live execution, pass live=True
and set environment var QNME_LIVE_SECRET to a configured token (prevents accidental live runs).
"""

import asyncio
import logging
import os
from typing import Any, Optional

from modules.qnme.genome_numba import GenomeNumPyEngine
from modules.qnme.regime import RegimeEngine
from modules.qnme.strategy_pool import StrategyPool
from modules.qnme.gates import GatePipeline
from modules.qnme.meta_controller import MetaController
from modules.qnme.macro_intel import MacroIntel
from modules.qnme.risk import RiskEngine
from modules.qnme.anomaly import detect_anomaly
from modules.qnme.override import MetaCognitiveOverride

logger = logging.getLogger(__name__)

# Attempt to import real WsProvider / OrderManager; fallback to None for shadow testing
try:
    from modules.dhan.ws_provider import WsProvider
except Exception:
    WsProvider = None

try:
    from modules.order.manager import OrderManager
except Exception:
    OrderManager = None

class LiveOrchestrator:
    def __init__(self, live: bool = False, live_secret: Optional[str] = None):
        self.live = live
        self._live_secret = live_secret or os.environ.get("QNME_LIVE_SECRET")
        if self.live and not self._live_secret:
            raise RuntimeError("Live orchestrator requires QNME_LIVE_SECRET environment variable or live_secret param")
        # Layers
        self.genome = GenomeNumPyEngine(window=2048)
        self.regime = RegimeEngine()
        self.pool = StrategyPool()
        self.gates = GatePipeline()
        self.meta = MetaController()
        self.macro = MacroIntel()
        self.risk = RiskEngine()
        self.override = MetaCognitiveOverride(risk_engine=self.risk)
        # Execution
        self.order_manager = OrderManager(":memory:", None) if OrderManager is not None else None
        self._ws = None

    async def start_ws(self, uri: str, inbound_cb=None, *args, **kwargs):
        if WsProvider is None:
            logger.warning("WsProvider not available; start with external tick source.")
            return
        inbound_cb = inbound_cb or (lambda msg: asyncio.create_task(self._on_raw_tick(msg)))
        self._ws = WsProvider(uri, inbound_cb=inbound_cb, *args, **kwargs)
        await self._ws.start()

    async def _on_raw_tick(self, raw: dict):
        """
        Expected format: {'symbol','price','size','side','ts','spread','volume'}
        Adapt as necessary to your provider format.
        """
        try:
            await self.on_tick(raw)
        except Exception:
            logger.exception("on_tick failed")

    async def on_tick(self, tick: dict):
        # feed genome
        self.genome.on_trade(tick)
        genome_vec = self.genome.compute_genome()
        # regime
        rlabel, rconf = self.regime.predict(genome_vec)
        regime = {"name": rlabel, "conf": rconf}
        # strategies
        candidates = self.pool.on_tick_all(tick, genome_vec, regime)
        validated = []
        for c in candidates:
            ok, _ = self.gates.validate(c, tick, genome_vec, (rlabel, rconf))
            if ok:
                validated.append(c)
        weights = self.meta.aggregate(validated, (rlabel, rconf))
        # anomaly + override
        anomaly_flag, reason = detect_anomaly(genome_vec, tick)
        override_decision = self.override.evaluate(regime, anomaly_flag, {})
        if override_decision["action"] != "allow":
            logger.warning("Override triggered: %s", override_decision)
            return
        # decide orders
        orders = []
        for sid, w in weights.items():
            if w <= 0.0:
                continue
            orders.append({
                "strategy_id": sid,
                "symbol": tick.get("symbol"),
                "side": "BUY" if w > 0 else "SELL",
                "size": abs(float(w)),
                "price": tick.get("price")
            })
        if self.live:
            # send to OrderManager (if available). require explicit secret
            if not self._live_secret:
                logger.error("Attempted live execution without secret.")
                return
            if self.order_manager is None:
                logger.error("OrderManager not available; cannot send live orders.")
                return
            for o in orders:
                try:
                    self.order_manager.create_and_send(o["symbol"], o["side"], o["size"], price=o["price"])
                    logger.info("Sent live order %s", o)
                except Exception:
                    logger.exception("Failed to send live order")
        else:
            # shadow logs
            for o in orders:
                logger.info("SHADOW ORDER: %s", o)

    async def stop(self):
        if self._ws:
            await self._ws.stop()
