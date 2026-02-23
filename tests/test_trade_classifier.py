import pytest
from datetime import datetime
from zoneinfo import ZoneInfo
from qaai_system.execution.trade_classifier import TradeClassifier

IST = ZoneInfo("Asia/Kolkata")


@pytest.fixture
def classifier():
    return TradeClassifier()


def test_intraday_classification_rule_based(classifier):
    t = datetime(2025, 1, 1, 10, 0, tzinfo=IST)  # 10:00 AM IST
    assert classifier.classify_trade(entry_time=t) == "INTRADAY"


def test_swing_classification_rule_based(classifier):
    t = datetime(2025, 1, 1, 15, 0, tzinfo=IST)  # 3:00 PM IST
    assert classifier.classify_trade(entry_time=t) == "SWING"


def test_entry_allowed_intraday(classifier):
    t = datetime(2025, 1, 1, 14, 30, tzinfo=IST)  # 2:30 PM IST
    assert classifier.is_entry_allowed("INTRADAY", entry_time=t) is True


def test_entry_not_allowed_intraday(classifier):
    t = datetime(2025, 1, 1, 15, 0, tzinfo=IST)  # 3:00 PM IST
    assert classifier.is_entry_allowed("INTRADAY", entry_time=t) is False


def test_force_exit_intraday(classifier):
    t = datetime(2025, 1, 1, 15, 20, tzinfo=IST)  # 3:20 PM IST
    assert classifier.should_force_exit("INTRADAY", current_time=t) is True


def test_no_force_exit_swing(classifier):
    t = datetime(2025, 1, 1, 15, 20, tzinfo=IST)
    assert classifier.should_force_exit("SWING", current_time=t) is False
