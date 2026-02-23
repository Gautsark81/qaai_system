# core/reproducibility/vault_service.py

from __future__ import annotations
from .vault_store import VaultStore
from .vault_models import BacktestReproducibilityRecord


class VaultService:

    def __init__(self, store: VaultStore):
        self.store = store

    def register_record(
        self,
        hypothesis_id: str,
        hypothesis_hash: str,
        data_hash: str,
        feature_hash: str,
        parameter_hash: str,
        code_hash: str,
        env_hash: str,
        ssr_hash: str,
    ) -> str:

        record = BacktestReproducibilityRecord.create(
            hypothesis_id=hypothesis_id,
            hypothesis_hash=hypothesis_hash,
            data_hash=data_hash,
            feature_hash=feature_hash,
            parameter_hash=parameter_hash,
            code_hash=code_hash,
            env_hash=env_hash,
            ssr_hash=ssr_hash,
        )

        self.store.append(record)
        return record.record_id