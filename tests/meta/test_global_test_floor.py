from pathlib import Path


def test_global_test_floor(request):
    """
    Guards against accidental mass deletion of tests.

    Enforced ONLY when the full test suite is collected.
    Scoped runs (e.g. pytest tests/meta/) are ignored safely.
    """
    MIN_TOTAL_TESTS = 900

    collected = request.session.items

    # Detect whether non-meta tests were collected
    non_meta_tests = [
        item for item in collected
        if Path(item.fspath).parts[-2] != "meta"
    ]

    # If only meta tests are present, this is a scoped run → ignore
    if not non_meta_tests:
        return

    assert len(collected) >= MIN_TOTAL_TESTS, (
        f"Global test count dropped below {MIN_TOTAL_TESTS}: "
        f"found {len(collected)}"
    )
