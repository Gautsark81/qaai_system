# infra/queues.py
"""
Async queue utilities. Phase-0: in-memory AsyncQueue with optional simple persistence.
Persistence format: newline-delimited JSON for simple resume.
"""

import asyncio
import json
from pathlib import Path
from typing import Optional, Any
import logging

logger = logging.getLogger("queues")


class PersistentQueue:
    def __init__(self, persist_path: Optional[str] = None):
        self._queue = asyncio.Queue()
        self._persist_path = Path(persist_path) if persist_path else None
        if self._persist_path and self._persist_path.exists():
            # load persisted items
            try:
                with open(self._persist_path, "r", encoding="utf8") as f:
                    for line in f:
                        item = json.loads(line.strip())
                        self._queue.put_nowait(item)
            except Exception:
                logger.exception("failed to load persisted queue")

    async def put(self, item: Any):
        await self._queue.put(item)
        if self._persist_path:
            # append to file
            try:
                with open(self._persist_path, "a", encoding="utf8") as f:
                    f.write(json.dumps(item, default=str) + "\n")
            except Exception:
                logger.exception("failed to persist queue item")

    async def get(self) -> Any:
        item = await self._queue.get()
        # Note: persistence cleanup (removing first line) is not implemented for Phase-0.
        return item

    def qsize(self) -> int:
        return self._queue.qsize()

    def empty(self) -> bool:
        return self._queue.empty()


# Synchronous wrapper (for convenience)
class AsyncQueueAdapter:
    def __init__(self, queue: PersistentQueue):
        self._q = queue

    async def put_now(self, item):
        await self._q.put(item)

    async def get_now(self):
        return await self._q.get()
