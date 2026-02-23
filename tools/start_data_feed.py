# Path: tools/start_data_feed.py
"""Starter script to launch the Dhan v2 feed process with connection-count guard.

This script:
- Loads .env
- Validates token/clientId via src.config
- Creates a per-clientId lockfile in temp to avoid opening more than MAX_WS_CONNECTIONS concurrently
- Starts the Dhan feed in background (execution via src.router.start_dhan_v2_feed)
"""
import os
import signal
import time
import logging
import tempfile
import atexit
from pathlib import Path

from dotenv import load_dotenv
load_dotenv()

from src.config import config
from src.logging_config import configure_logging
from src.router import start_dhan_v2_feed, stop_dhan_v2_feed

configure_logging(config.LOG_LEVEL)
logger = logging.getLogger("tools.start_data_feed")

_lockfile_path: Path | None = None

def _get_lock_dir() -> Path:
    td = Path(tempfile.gettempdir())
    d = td / "qaai_dhan_locks"
    d.mkdir(parents=True, exist_ok=True)
    return d

def _existing_locks_for_client(client_id: str):
    d = _get_lock_dir()
    pattern = f"qaai_dhan_conn_{client_id}_*.lock"
    return list(d.glob(pattern))

def _create_lock(client_id: str) -> Path:
    """Create a lockfile named by client_id and PID. Return path."""
    d = _get_lock_dir()
    pid = os.getpid()
    path = d / f"qaai_dhan_conn_{client_id}_{pid}.lock"
    path.write_text(f"pid:{pid}\nstarted:{time.time()}\n")
    return path

def _remove_lock(path: Path | None):
    try:
        if path and path.exists():
            path.unlink()
            logger.info("Removed connection lock %s", path)
    except Exception:
        logger.exception("Failed to remove lockfile")

def _register_exit_cleanup(path: Path | None):
    if not path:
        return
    def _cleanup():
        _remove_lock(path)
    atexit.register(_cleanup)
    # also signal handlers
    def _term(signum, frame):
        logger.info("Received shutdown signal %s", signum)
        _cleanup()
        raise SystemExit(0)
    signal.signal(signal.SIGINT, _term)
    signal.signal(signal.SIGTERM, _term)

def main():
    global _lockfile_path
    logger.info("Starting data feed (client_id=%s)", config.DHAN_CLIENT_ID or "<missing>")

    # Basic validation
    token = config.selected_token
    client_id = config.DHAN_CLIENT_ID
    if not client_id:
        logger.error("DHAN_CLIENT_ID missing in environment. Please set DHAN_CLIENT_ID.")
        return
    if not token:
        logger.error("No DHAN token selected. Set DHAN_ACCESS_TOKEN or DHAN_ACCESS_TOKEN_LIVE/PAPER in .env.")
        return

    # check existing locks
    locks = _existing_locks_for_client(client_id)
    logger.info("Existing local feed locks for client %s: %d (max allowed %d)", client_id, len(locks), config.MAX_WS_CONNECTIONS)
    if len(locks) >= config.MAX_WS_CONNECTIONS:
        logger.error(
            "There are already %d local feed instances for client %s. Aborting to avoid exceeding the allowed concurrent connections (%d).",
            len(locks),
            client_id,
            config.MAX_WS_CONNECTIONS,
        )
        logger.error("If these processes are stale, remove lock files under %s", _get_lock_dir())
        return

    # create lock for this process and register cleanup
    _lockfile_path = _create_lock(client_id)
    logger.info("Created connection lock %s", _lockfile_path)
    _register_exit_cleanup(_lockfile_path)

    # start feed
    feed = start_dhan_v2_feed(token=token, client_id=client_id, instruments=config.DHAN_V2_INSTRUMENTS)
    if not feed:
        logger.error("Feed failed to start. Removing lock and exiting.")
        _remove_lock(_lockfile_path)
        return

    logger.info("Feed running; press Ctrl-C to stop.")
    # main loop — keep process alive until killed
    try:
        while True:
            time.sleep(1)
    except SystemExit:
        logger.info("Shutting down feed")
        stop_dhan_v2_feed()
        _remove_lock(_lockfile_path)
    except Exception:
        logger.exception("Unexpected exception; stopping feed")
        stop_dhan_v2_feed()
        _remove_lock(_lockfile_path)

if __name__ == "__main__":
    main()
