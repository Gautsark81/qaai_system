from audit.compliance_assertions import compliance_assertions


def test_compliance_assertions_complete():
    a = compliance_assertions()
    assert all(a.values())
