from pathlib import Path
from core.reproducibility.vault_store import VaultStore
from core.reproducibility.vault_models import BacktestReproducibilityRecord


def test_append_and_retrieve(tmp_path: Path):
    store = VaultStore(tmp_path / "vault.jsonl")

    record = BacktestReproducibilityRecord.create(
        hypothesis_id="H1",
        hypothesis_hash="h",
        data_hash="d",
        feature_hash="f",
        parameter_hash="p",
        code_hash="c",
        env_hash="e",
        ssr_hash="s",
    )

    store.append(record)

    records = store.get_all()
    assert len(records) == 1
    assert records[0]["hypothesis_id"] == "H1"