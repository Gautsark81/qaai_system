from domain.graduation.graduation_level import GraduationLevel


def test_graduation_levels():
    assert GraduationLevel.PRODUCTION.value == "PRODUCTION"
