from pathlib import Path
from core.reproducibility.vault_store import VaultStore
from core.reproducibility.vault_service import VaultService


def test_vault_service_register(tmp_path: Path):
    store = VaultStore(tmp_path / "vault.jsonl")
    service = VaultService(store)

    record_id = service.register_record(
        hypothesis_id="H1",
        hypothesis_hash="hh",
        data_hash="dd",
        feature_hash="ff",
        parameter_hash="pp",
        code_hash="cc",
        env_hash="ee",
        ssr_hash="ss",
    )

    records = store.get_all()
    assert records[0]["record_id"] == record_id