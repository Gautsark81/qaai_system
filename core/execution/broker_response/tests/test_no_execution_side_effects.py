from core.execution.broker_response.policy import policy_for


def test_policy_has_no_execution_authority():
    policy = policy_for.__wrapped__ if hasattr(policy_for, "__wrapped__") else policy_for
    forbidden = {"execute", "retry", "submit", "cancel"}

    for name in forbidden:
        assert not hasattr(policy, name)
