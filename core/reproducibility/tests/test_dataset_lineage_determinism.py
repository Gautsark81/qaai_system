from core.reproducibility.dataset_provenance import DatasetProvenance
from core.reproducibility.dataset_lineage_hash import DatasetLineageHasher


def test_symbol_order_does_not_change_hash():
    p1 = DatasetProvenance(
        source_type="db",
        source_identifier="prices_table",
        snapshot_id="snap-1",
        symbol_list=["B", "A"],
        start_date="2023-01-01",
        end_date="2023-02-01",
        record_count=200,
    )

    p2 = DatasetProvenance(
        source_type="db",
        source_identifier="prices_table",
        snapshot_id="snap-1",
        symbol_list=["A", "B"],
        start_date="2023-01-01",
        end_date="2023-02-01",
        record_count=200,
    )

    assert DatasetLineageHasher.hash(p1) == DatasetLineageHasher.hash(p2)