from pathlib import Path


MIN_PHASE_11_TESTS = 5


def test_phase_11_minimum_test_count():
    """
    CI guard: Phase-11 must maintain a minimum number of tests.
    Prevents silent erosion of coverage.
    """
    phase_11_dir = Path("tests/phase_11")
    test_files = list(phase_11_dir.glob("test_*.py"))

    assert len(test_files) >= MIN_PHASE_11_TESTS, (
        f"Phase-11 requires at least {MIN_PHASE_11_TESTS} tests, "
        f"found {len(test_files)}"
    )
