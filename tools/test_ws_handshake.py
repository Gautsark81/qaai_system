# Path: tools/test_ws_handshake.py
"""Simple tester for the Dhan WebSocket handshake.

Usage:
  python -m tools.test_ws_handshake "wss://api-feed.dhan.co?version=2&token=...&clientId=...&authType=2"
"""
import asyncio
import json
import logging
import sys

import websockets
from websockets.exceptions import ConnectionClosedError, InvalidStatus

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("tools.test_ws_handshake")

async def run_test(ws_url, payload_json):
    try:
        logger.info("Connecting to: %s", ws_url)
        async with websockets.connect(ws_url) as ws:
            logger.info("Connected. Sending payload: %s", payload_json)
            await ws.send(payload_json)
            try:
                msg = await asyncio.wait_for(ws.recv(), timeout=5)
                logger.info("Received: %s", msg)
            except asyncio.TimeoutError:
                logger.info("No message received within timeout; connection stayed open.")
    except InvalidStatus as isc:
        logger.error("InvalidStatus during connect: %s", isc)
    except ConnectionClosedError as cce:
        logger.error("ConnectionClosedError: code=%s reason=%s exc=%s", getattr(cce, 'code', None), getattr(cce, 'reason', None), cce)
    except Exception as ex:
        logger.exception("Exception during handshake: %s", ex)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m tools.test_ws_handshake \"wss://...\"")
        sys.exit(1)
    ws_url = sys.argv[1]
    payload = {
        "RequestCode": 15,
        "InstrumentCount": 2,
        "InstrumentList": [
            {"ExchangeSegment": "NSE_EQ", "SecurityId": "1333"},
            {"ExchangeSegment": "BSE_EQ", "SecurityId": "532540"},
        ],
    }
    asyncio.run(run_test(ws_url, json.dumps(payload)))
