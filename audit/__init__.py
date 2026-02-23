# qaai_system/audit/__init__.py

"""
Audit package initializer.
Provides access to audit_charts submodule.
"""

import importlib


def __getattr__(name):
    if name == "audit_charts":
        return importlib.import_module(".audit_charts", __name__)
    raise AttributeError(f"module {__name__!r} has no attribute {name!r}")


__all__ = ["audit_charts"]
