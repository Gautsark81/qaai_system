import json
from modules.persistence.db import Database

class TelemetryRepository:
    def __init__(self, db: Database):
        self.db = db

    def persist(self, *, strategy_id, step, category, snapshot):
        self.db.insert(
            strategy_id=strategy_id,
            step=step,
            category=category,
            payload=json.dumps(snapshot.__dict__),
        )
