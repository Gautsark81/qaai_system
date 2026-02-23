import sqlite3

class Database:
    def __init__(self, path="qaai.db"):
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self._init()

    def _init(self):
        self.conn.execute("""
        CREATE TABLE IF NOT EXISTS telemetry (
            strategy_id TEXT,
            step INTEGER,
            category TEXT,
            payload TEXT
        )
        """)
        self.conn.commit()

    def insert(self, strategy_id, step, category, payload):
        self.conn.execute(
            "INSERT INTO telemetry VALUES (?, ?, ?, ?)",
            (strategy_id, step, category, payload),
        )
        self.conn.commit()
