from pathlib import Path


def test_phase_maturity_report(capsys):
    """
    CI-visible report of phase maturity.
    Purely informational.
    """

    phases = {
        9: Path("tests/phase_9"),
        10: Path("tests/phase_10"),
        11: Path("tests/phase_11"),
    }

    report = {}
    for phase, path in phases.items():
        tests = list(path.glob("test_*.py"))
        report[phase] = len(tests)

    print("\nPHASE MATURITY REPORT")
    for phase in sorted(report):
        print(f"Phase {phase}: {report[phase]} test files")

    # No assertion — visibility only
    assert report[11] >= 5
