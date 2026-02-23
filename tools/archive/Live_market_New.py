#!/usr/bin/env python3
"""
Entry point for the live market process.

- Loads dotenv (merges .env + deploy/.env if present)
- Creates DhanSafeClient and Router
- Exposes a tiny FastAPI health endpoint (optional)
- Async-safe, structured logging, graceful shutdown
"""
import asyncio
import logging
import os
import signal
from contextlib import asynccontextmanager

from dotenv import load_dotenv, find_dotenv
from fastapi import FastAPI
import uvicorn

# local services
from services.dhan_client_safe import DhanSafeClient
from services.router import Router
from services.metrics import start_prometheus_push

# Load .env files (priority: ./deploy/.env -> .env)
deploy_env = os.path.join(os.getcwd(), "deploy", ".env")
if os.path.exists(deploy_env):
    load_dotenv(deploy_env, override=False)
# fallback to repository root .env
load_dotenv(override=False)

LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO").upper()
logging.basicConfig(
    level=LOG_LEVEL,
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
)
logger = logging.getLogger("live_market")

app = FastAPI(title="Live Market Service", docs_url=None, redoc_url=None)
shutdown_event = asyncio.Event()

@app.get("/healthz")
async def healthz():
    return {"status": "ok", "env": os.getenv("TRADING_ENV", "unknown")}

def _install_signal_handlers(loop):
    def _on_signal(sig):
        logger.info("Received signal %s, shutting down...", sig)
        shutdown_event.set()
    for s in (signal.SIGINT, signal.SIGTERM):
        try:
            loop.add_signal_handler(s, lambda s=s: _on_signal(s))
        except NotImplementedError:
            # Windows fallback or restricted environments
            signal.signal(s, lambda *_: _on_signal(s))

@asynccontextmanager
async def lifespan_context():
    # Start any background infra (metrics push, etc)
    prom = None
    try:
        if os.getenv("PROMETHEUS_PUSHGATEWAY"):
            prom = start_prometheus_push()
        yield
    finally:
        if prom:
            prom.close()

async def main_loop():
    # Client config from env
    max_retries = int(os.getenv("RECONNECT_MAX_RETRIES", "5"))
    backoff = float(os.getenv("RECONNECT_BACKOFF_BASE", "1"))
    dhan_client = DhanSafeClient(
        api_key=os.getenv("DHAN_ACCESS_TOKEN") or os.getenv("DHAN_ACCESS_TOKEN_LIVE"),
        api_secret=os.getenv("DHAN_CLIENT_ID"),
        client_id=os.getenv("DHAN_CLIENT_ID"),
        max_retries=max_retries,
        backoff_base=backoff
    )

    router = Router(dhan_client)

    await router.start()          # starts internal market loop task
    logger.info("Router started")

    # wait for shutdown
    await shutdown_event.wait()
    logger.info("shutdown event received, stopping router...")
    await router.stop()
    await dhan_client.close()
    logger.info("clean shutdown complete")

def run_uvicorn_in_bg():
    # run FastAPI health server in a background thread/process
    port = int(os.getenv("HEALTH_PORT", 8000))
    config = uvicorn.Config(app, host="0.0.0.0", port=port, log_level="warning")
    server = uvicorn.Server(config)
    return server

def main():
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    _install_signal_handlers(loop)

    # start uvicorn health server in background task (optional)
    if os.getenv("ENABLE_HEALTH", "true").lower() in ("true", "1", "yes"):
        import threading
        server = run_uvicorn_in_bg()
        t = threading.Thread(target=server.run, daemon=True)
        t.start()
        logger.info("Health endpoint started on port %s", os.getenv("HEALTH_PORT", "8000"))

    try:
        loop.run_until_complete(main_loop())
    except Exception as e:
        logger.exception("Unhandled exception in top-level main: %s", e)
    finally:
        loop.run_until_complete(loop.shutdown_asyncgens())
        loop.close()
        logger.info("process exit")

if __name__ == "__main__":
    main()
