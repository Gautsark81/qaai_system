import json
import os
from typing import Dict, Iterable


class PaperTradeStore:
    def __init__(self, path: str):
        self.path = path
        os.makedirs(os.path.dirname(path), exist_ok=True)

    def append(self, trade: Dict):
        tmp = self.path + ".tmp"

        # 1️⃣ Read existing content (if any)
        existing = ""
        if os.path.exists(self.path):
            with open(self.path, "r", encoding="utf-8") as f:
                existing = f.read()

        # 2️⃣ Write existing + new trade to temp file
        with open(tmp, "w", encoding="utf-8") as f:
            if existing:
                f.write(existing)
            f.write(json.dumps(trade) + "\n")
            f.flush()
            os.fsync(f.fileno())

        # 3️⃣ Atomic replace
        os.replace(tmp, self.path)

    def replay(self) -> Iterable[Dict]:
        if not os.path.exists(self.path):
            return []

        with open(self.path, "r", encoding="utf-8") as f:
            for line in f:
                yield json.loads(line)
