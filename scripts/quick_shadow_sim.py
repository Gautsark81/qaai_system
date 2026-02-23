# scripts/quick_shadow_sim.py
"""
Quick shadow simulation for evaluating candidate strategies and mutation outputs.
This script demonstrates how to feed a stored replay slice (list of ticks)
to a Strategy instance or a config.
"""
import random
from modules.qnme.orchestrator import QNMEOrchestrator, list_tick_source
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

async def run_demo():
    # generate simple synthetic ticks
    ticks = [{"ts": i, "symbol": "FOO", "price": 100.0 + random.gauss(0,1), "size": random.randint(1,5), "side": random.choice(["B","S"]), "spread": 0.01, "volume": 100} for i in range(200)]
    orch = QNMEOrchestrator(shadow=True)
    await orch.run_live_loop(list_tick_source(ticks, delay=0.0), stop_after=1.0)

if __name__ == "__main__":
    asyncio.run(run_demo())
