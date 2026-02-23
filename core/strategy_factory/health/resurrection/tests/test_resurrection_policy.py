from core.strategy_factory.health.resurrection.policy import ResurrectionPolicy


def test_eligible_strategy_can_be_resurrected(mock_record, mock_decay):
    assert ResurrectionPolicy.is_eligible(mock_record, mock_decay)
