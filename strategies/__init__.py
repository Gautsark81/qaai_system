# strategies/__init__.py
"""
+strategies package init.
+This package contains strategy implementations and shims for backward compatibility.
+"""
from .strategy_base import *  # re-export base items for convenience

__all__ = ["strategy_base"]
