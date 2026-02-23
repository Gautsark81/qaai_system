# qaai_system/signal_engine/__init__.py

"""
Signal Engine Package

Compatibility Layer:
- Ensures legacy imports do not break pytest collection.
- Maintains stable public API boundary.
"""

from .signal_engine_supercharged import SignalEngineSupercharged

__all__ = [
    "SignalEngineSupercharged",
    "persist_model",
]


def persist_model(*args, **kwargs):
    """
    Legacy compatibility shim.

    This function existed in older architecture versions.
    It is preserved to avoid breaking archived tools/tests.

    Current system uses structured model registry + model ops.
    """
    raise NotImplementedError(
        "persist_model is deprecated in the current architecture. "
        "Use the Model Ops registry layer instead."
    )