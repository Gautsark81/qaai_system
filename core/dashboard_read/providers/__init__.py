# core/dashboard_read/providers/__init__.py

"""
Dashboard read providers.

This package intentionally exposes no side effects.

All providers must be imported explicitly:
    from core.dashboard_read.providers.capital import build_capital_state

We do NOT import submodules here to avoid pytest
package duplication and module identity splits.
"""

__all__ = []