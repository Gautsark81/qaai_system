from pathlib import Path
import pytest
from core.runtime.release_lock import ReleaseLock


def test_release_lock_blocks_change(tmp_path: Path):
    f = tmp_path / "a.py"
    f.write_text("x = 1")

    # compute hash explicitly (no walrus)
    hasher = ReleaseLock(tmp_path, expected_hash="")
    expected_hash = hasher._compute_hash()

    lock = ReleaseLock(tmp_path, expected_hash=expected_hash)

    # mutate file
    f.write_text("x = 2")

    with pytest.raises(RuntimeError):
        lock.verify()
