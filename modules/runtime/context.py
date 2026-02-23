# modules/runtime/context.py

from modules.runtime.flags import RuntimeFlags


# SINGLE SOURCE OF TRUTH
_RUNTIME_FLAGS = RuntimeFlags()


def get_runtime_flags() -> RuntimeFlags:
    """
    Read-only access to runtime flags.
    Flags must NEVER gate core logic.
    """
    return _RUNTIME_FLAGS
