# core/safety/tests/test_no_env_kill_bypass.py
import os
import pytest


FORBIDDEN_TOKENS = (
    "DISABLE_KILL_SWITCH",
    "SKIP_KILL_CHECK",
)

EXCLUDE_FILES = {
    os.path.basename(__file__),  # exclude this test file itself
}

EXCLUDE_DIRS = {
    "__pycache__",
    ".venv",
    "venv",
    ".git",
    ".pytest_cache",
}


def test_no_disable_kill_env_variable_in_repo():
    """
    Hard safety invariant:
    No environment-variable-based kill-switch bypasses are allowed
    anywhere in the repository.

    This test intentionally scans the entire codebase and fails fast.
    """

    root = os.path.abspath(os.environ.get("PROJECT_ROOT", "."))

    for dirpath, dirnames, filenames in os.walk(root):
        # prune excluded directories
        dirnames[:] = [d for d in dirnames if d not in EXCLUDE_DIRS]

        for filename in filenames:
            if filename in EXCLUDE_FILES:
                continue

            if not filename.endswith((".py", ".sh", ".env", ".yaml", ".yml")):
                continue

            path = os.path.join(dirpath, filename)

            try:
                with open(path, "r", encoding="utf-8") as f:
                    content = f.read()
            except (UnicodeDecodeError, OSError):
                # binary or unreadable file — ignore safely
                continue

            for token in FORBIDDEN_TOKENS:
                assert token not in content, (
                    f"❌ Forbidden kill-switch bypass token '{token}' "
                    f"found in file: {path}"
                )
