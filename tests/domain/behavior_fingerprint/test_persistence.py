from datetime import datetime
from domain.behavior_fingerprint.persistence import FingerprintRecord
from domain.behavior_fingerprint.enums import LifecycleStage


def test_fingerprint_record_creation():
    record = FingerprintRecord(
        strategy_id="s1",
        fingerprint_version=1,
        fingerprint=None,  # storage contract test only
        parent_fingerprint_version=None,
        lifecycle_stage=LifecycleStage.GENERATED,
        created_ts=datetime.utcnow(),
        created_by="system",
    )

    assert record.fingerprint_version == 1
