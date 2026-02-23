# modules/qnme/orchestrator.py
"""
A lightweight top-level orchestrator that wires together QNME layers in shadow mode.
By default this will not send live orders. It demonstrates how to plug into
your existing DhanFetcher (modules.dhan.ws_provider) and OrderManager.
"""

import asyncio
import logging
from typing import Any

from modules.qnme.genome import GenomeEngine
from modules.qnme.regime import RegimeEngine
from modules.qnme.strategy_pool import StrategyPool
from modules.qnme.gates import GatePipeline
from modules.qnme.meta_controller import MetaController
from modules.qnme.macro_intel import MacroIntel
from modules.qnme.risk import RiskEngine
from modules.qnme.anomaly import detect_anomaly
from modules.qnme.override import MetaCognitiveOverride

logger = logging.getLogger(__name__)

class QNMEOrchestrator:
    def __init__(self, shadow: bool = True):
        self.shadow = shadow
        self.genome = GenomeEngine(window=256)
        self.regime = RegimeEngine()
        self.pool = StrategyPool()
        self.gates = GatePipeline()
        self.meta = MetaController()
        self.macro = MacroIntel()
        self.risk = RiskEngine()
        self.override = MetaCognitiveOverride(risk_engine=self.risk)

    async def on_tick(self, tick: dict):
        # 1) feed genome
        self.genome.on_trade(tick)
        genome_vec = self.genome.compute_genome()

        # 2) regime
        regime_label, regime_conf = self.regime.predict(genome_vec)
        regime = (regime_label, regime_conf)

        # 3) strategy candidates
        candidates = self.pool.on_tick_all(tick, genome_vec, regime)

        # 4) gate pipeline
        validated = []
        for c in candidates:
            ok, details = self.gates.validate(c, tick, genome_vec, regime)
            if ok:
                validated.append(c)

        # 5) meta controller
        weights = self.meta.aggregate(validated, regime)

        # 6) anomaly & override checks
        anomaly_flag, reason = detect_anomaly(genome_vec, tick)
        override_decision = self.override.evaluate({"name": regime_label, "conf": regime_conf}, anomaly_flag, {})

        # 7) risk checks & execution (shadow by default)
        if override_decision["action"] != "allow":
            logger.warning("Override action: %s, reason=%s", override_decision["action"], override_decision["reason"])
            return

        # produce shadow orders (log)
        orders = []
        for sid, w in weights.items():
            if w <= 0.0:
                continue
            # craft a simple order object for shadow
            orders.append({
                "strategy_id": sid,
                "symbol": tick.get("symbol"),
                "side": "BUY",
                "size": w,
                "price": tick.get("price")
            })
        if self.shadow:
            for o in orders:
                logger.info("SHADOW ORDER: %s", o)
        else:
            # live execution path (call your OrderManager / ExecutionEngine)
            logger.info("Would send %d orders live", len(orders))
        # update risk with dummy PnL 0 for example
        self.risk.update_returns(0.0)

    async def run_live_loop(self, tick_source, stop_after: float = None):
        """
        tick_source: async iterator yielding ticks
        stop_after: seconds to run (None -> forever)
        """
        start = asyncio.get_event_loop().time()
        async for tick in tick_source:
            await self.on_tick(tick)
            if stop_after and (asyncio.get_event_loop().time() - start) > stop_after:
                break

# Small helper: example tick source from list
async def list_tick_source(ticks, delay=0.0):
    for t in ticks:
        yield t
        if delay:
            await asyncio.sleep(delay)

if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    orch = QNMEOrchestrator(shadow=True)
    # example synthetic ticks
    ticks = [{"ts": i, "symbol": "FOO", "price": 100.0 + i, "size": 1, "side": "B", "spread": 0.01, "volume": 100} for i in range(50)]
    async def demo():
        await orch.run_live_loop(list_tick_source(ticks, 0.01), stop_after=1.0)
    asyncio.run(demo())
