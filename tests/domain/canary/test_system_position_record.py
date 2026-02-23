from domain.canary.system_position_record import SystemPositionRecord


def test_system_position_record():
    r = SystemPositionRecord("NIFTY", 2, 19500)
    assert r.symbol == "NIFTY"
