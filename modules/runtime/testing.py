# modules/runtime/testing.py

from contextlib import contextmanager
from modules.runtime.flags import RuntimeFlags
import modules.runtime.context as context


@contextmanager
def override_runtime_flags(**kwargs):
    """
    Test-only override for runtime flags.
    Does NOT mutate frozen instances.
    """
    original = context._RUNTIME_FLAGS
    try:
        context._RUNTIME_FLAGS = RuntimeFlags(**{
            **original.__dict__,
            **kwargs,
        })
        yield
    finally:
        context._RUNTIME_FLAGS = original
