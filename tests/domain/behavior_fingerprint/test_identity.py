from datetime import datetime
from domain.behavior_fingerprint.identity import IdentityFingerprint
from domain.behavior_fingerprint.enums import StrategyFamily, GenerationSource


def test_identity_fingerprint_creation():
    fp = IdentityFingerprint(
        strategy_id="strat_001",
        strategy_family=StrategyFamily.TREND,
        generation_source=GenerationSource.HUMAN,
        code_hash="abc123",
        parameter_hash="param456",
        creation_ts=datetime.utcnow(),
    )

    assert fp.strategy_id == "strat_001"
    assert fp.strategy_family == StrategyFamily.TREND
