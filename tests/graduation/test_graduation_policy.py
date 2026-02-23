from domain.graduation.graduation_policy import GraduationPolicy


def test_graduation_policy_fields():
    p = GraduationPolicy(0.75, 30, 0.12, 200)
    assert p.min_live_days == 30
