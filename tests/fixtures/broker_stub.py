# tests/fixtures/broker_stub.py
import asyncio
from typing import Dict, Any

class BrokerStub:
    def __init__(self, partial_fill_qty: int = 0, fail_after: int = 0):
        self.partial_fill_qty = partial_fill_qty
        self.fail_after = fail_after
        self.calls = 0

    async def place_limit(self, order: Dict[str, Any]) -> Dict[str, Any]:
        self.calls += 1
        await asyncio.sleep(0.005)
        if self.fail_after and self.calls > self.fail_after:
            raise RuntimeError("Simulated broker failure")
        return {"order_id": f"stub-{self.calls}", "filled": self.partial_fill_qty, "status":"accepted"}

    async def place_market(self, order: Dict[str, Any]) -> Dict[str, Any]:
        await asyncio.sleep(0.002)
        return {"order_id": f"mkt-{int(asyncio.get_event_loop().time()*1000)}", "filled": order.get("qty", 0), "status":"filled"}
