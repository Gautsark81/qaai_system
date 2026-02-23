"""
WebSocket dashboard that subscribes to Redis 'market:ticks' channel and
pushes messages to connected browser clients.

Provides:
 - GET /           -> simple HTML dashboard
 - GET /metrics    -> Prometheus metrics
 - /ws            -> WebSocket stream
"""

import os
import json
import logging
import asyncio
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from prometheus_client import Counter, generate_latest, CONTENT_TYPE_LATEST
import redis.asyncio as aioredis

logger = logging.getLogger("dashboard")
logger.setLevel(logging.INFO)

app = FastAPI(title="Market Dashboard")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379")
CHANNEL = os.getenv("REDIS_CHANNEL", "market:ticks")

# Prometheus metrics
ticks_received = Counter("qaai_ticks_received_total", "Total ticks received from Redis")

# in-memory set of websockets
clients = set()


@app.get("/metrics")
async def metrics():
    data = generate_latest()
    return HTMLResponse(content=data, media_type=CONTENT_TYPE_LATEST)


html = """
<!doctype html>
<html>
  <head>
    <title>Live Market Dashboard</title>
    <style>
      body { font-family: monospace; margin: 0; padding: 0; }
      #log { height: calc(100vh - 20px); overflow:auto; padding:10px; background:#111; color:#0f0; }
    </style>
  </head>
  <body>
    <div id="log"></div>
    <script>
      const log = document.getElementById('log');
      const ws = new WebSocket(`ws://${location.host}/ws`);
      ws.onopen = () => log.insertAdjacentHTML('beforeend', '<div>[connected]</div>');
      ws.onmessage = (ev) => {
        const msg = JSON.parse(ev.data);
        log.insertAdjacentHTML('beforeend', '<div>' + (new Date(msg.timestamp*1000).toISOString()) + ' ' + (msg.symbol||'') + ' ' + (msg.price||'') + '</div>');
        log.scrollTop = log.scrollHeight;
      };
      ws.onclose = () => log.insertAdjacentHTML('beforeend','<div>[closed]</div>');
    </script>
  </body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def index():
    return html


@app.websocket("/ws")
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        while True:
            # keep the connection alive — client doesn't send usually
            await asyncio.sleep(10)
    except WebSocketDisconnect:
        clients.remove(ws)


async def redis_to_ws():
    r = aioredis.from_url(REDIS_URL)
    pubsub = r.pubsub(ignore_subscribe_messages=True)
    await pubsub.subscribe(CHANNEL)
    logger.info("Dashboard subscribed to %s", CHANNEL)
    try:
        async for message in pubsub.listen():
            if message is None:
                await asyncio.sleep(0.01)
                continue
            if message.get("type") != "message":
                continue
            payload_raw = message.get("data")
            if isinstance(payload_raw, (bytes, bytearray)):
                try:
                    payload = json.loads(payload_raw.decode("utf-8"))
                except Exception:
                    payload = payload_raw.decode("utf-8")
            else:
                payload = payload_raw
            ticks_received.inc()
            # broadcast to websockets (fire and forget)
            data = json.dumps(payload)
            to_remove = []
            for c in set(clients):
                try:
                    await c.send_text(data)
                except Exception:
                    to_remove.append(c)
            for c in to_remove:
                clients.discard(c)
    finally:
        await pubsub.unsubscribe(CHANNEL)
        await r.close()


@app.on_event("startup")
async def startup_event():
    # start background redis listener
    loop = asyncio.get_event_loop()
    loop.create_task(redis_to_ws())
    logger.info("Dashboard started and listening for ticks")
