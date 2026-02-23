# infra/Dhan_websocket.py

import websocket
import json
import threading
import time
import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger("DhanWebSocket")

DHAN_ACCESS_TOKEN = os.getenv("DHAN_ACCESS_TOKEN")
SUBSCRIBED_INSTRUMENTS = os.getenv("WS_SYMBOLS", "RELIANCE,TCS").split(",")

# Static instrument map (You can replace this with CSV or API source)
INSTRUMENT_MAP = {
    "RELIANCE": 123456,  # Replace with real Dhan instrument IDs
    "TCS": 789012,
}

LTP_CACHE = {}


class DhanWebSocket:
    def __init__(self):
        self.ws_url = "wss://data-feed.dhan.co/feed"
        self.access_token = DHAN_ACCESS_TOKEN
        self.socket = None
        self.reconnect = True
        self.thread = None

    def on_message(self, ws, message):
        try:
            data = json.loads(message)
            instrument_token = str(data.get("instrument_token"))
            ltp = float(data.get("last_traded_price", 0))
            for symbol, token in INSTRUMENT_MAP.items():
                if str(token) == instrument_token:
                    LTP_CACHE[symbol] = ltp
                    logger.debug(f"[LTP] {symbol}: {ltp}")
        except Exception as e:
            logger.exception(f"Error parsing WebSocket message: {e}")

    def on_error(self, ws, error):
        logger.error(f"WebSocket Error: {error}")

    def on_close(self, ws, close_status_code, close_msg):
        logger.warning(f"WebSocket closed: {close_status_code} - {close_msg}")
        if self.reconnect:
            time.sleep(2)
            self.start()

    def on_open(self, ws):
        logger.info("WebSocket connection opened.")
        subscribe_payload = {
            "token": self.access_token,
            "data": [
                {"instrument_token": str(INSTRUMENT_MAP[s])}
                for s in SUBSCRIBED_INSTRUMENTS
                if s in INSTRUMENT_MAP
            ],
        }
        ws.send(json.dumps(subscribe_payload))
        logger.info(f"Subscribed to: {SUBSCRIBED_INSTRUMENTS}")

    def start(self):
        self.socket = websocket.WebSocketApp(
            self.ws_url,
            on_open=self.on_open,
            on_message=self.on_message,
            on_error=self.on_error,
            on_close=self.on_close,
        )
        self.thread = threading.Thread(target=self.socket.run_forever)
        self.thread.daemon = True
        self.thread.start()

    def stop(self):
        self.reconnect = False
        if self.socket:
            self.socket.close()
        if self.thread:
            self.thread.join()
