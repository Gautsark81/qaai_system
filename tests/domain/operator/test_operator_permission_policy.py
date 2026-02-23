from domain.operator.operator_permission_policy import OperatorPermissionPolicy


def test_operator_permission_policy():
    assert OperatorPermissionPolicy.allow("VIEW") is True
    assert OperatorPermissionPolicy.allow("EXECUTE") is False
