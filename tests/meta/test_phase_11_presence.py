from pathlib import Path


def test_phase_11_test_directory_exists():
    """
    Meta-test: Phase-11 must exist once project reaches Phase >=11.
    Prevents accidental deletion or renaming of test coverage.
    """
    phase_11_dir = Path("tests/phase_11")
    assert phase_11_dir.exists(), "tests/phase_11 directory is missing"
    assert phase_11_dir.is_dir(), "tests/phase_11 is not a directory"


def test_phase_11_has_tests():
    """
    Meta-test: Phase-11 must contain at least one test file.
    """
    phase_11_dir = Path("tests/phase_11")
    test_files = list(phase_11_dir.glob("test_*.py"))

    assert len(test_files) > 0, (
        "Phase-11 directory exists but contains no test files"
    )
