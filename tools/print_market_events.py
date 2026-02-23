# tools/print_market_events.py
import asyncio
import logging
import os
import signal
import sys
from src.config import config
from src.router import start_dhan_v2_feed, register_market_handler

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s: %(message)s")
logger = logging.getLogger("print_market_events")

def print_handler(event):
    # pretty print important fields
    print("EVENT:", event)

def main():
    token = config.DHAN_ACCESS_TOKEN
    client_id = config.DHAN_CLIENT_ID
    instruments = config.DHAN_V2_INSTRUMENTS

    if not token or not client_id:
        logger.error("Missing token / client_id in config")
        sys.exit(1)

    # Start feed
    feed = start_dhan_v2_feed(token=token, client_id=client_id, instruments=instruments, on_market_event=print_handler)
    # start in background
    feed.start_background()

    # Wait until ctrl-c
    loop = asyncio.get_event_loop()

    def _sig(_s, _f):
        logger.info("Shutdown signal received")
        feed.stop()
    for sig in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(sig, lambda s=sig: _sig(s, None))
        except NotImplementedError:
            # Windows event loop may not support add_signal_handler
            pass

    try:
        loop.run_forever()
    except KeyboardInterrupt:
        logger.info("Keyboard interrupt")
    finally:
        feed.stop()

if __name__ == "__main__":
    main()
