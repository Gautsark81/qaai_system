# core/reproducibility/vault_models.py

from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime
from uuid import uuid4
import pytz

IST = pytz.timezone("Asia/Kolkata")


@dataclass(frozen=True)
class BacktestReproducibilityRecord:
    record_id: str
    hypothesis_id: str
    hypothesis_hash: str
    data_hash: str
    feature_hash: str
    parameter_hash: str
    code_hash: str
    env_hash: str
    ssr_hash: str
    created_at: datetime

    @staticmethod
    def create(
        hypothesis_id: str,
        hypothesis_hash: str,
        data_hash: str,
        feature_hash: str,
        parameter_hash: str,
        code_hash: str,
        env_hash: str,
        ssr_hash: str,
    ) -> "BacktestReproducibilityRecord":
        return BacktestReproducibilityRecord(
            record_id=str(uuid4()),
            hypothesis_id=hypothesis_id,
            hypothesis_hash=hypothesis_hash,
            data_hash=data_hash,
            feature_hash=feature_hash,
            parameter_hash=parameter_hash,
            code_hash=code_hash,
            env_hash=env_hash,
            ssr_hash=ssr_hash,
            created_at=datetime.now(IST),
        )