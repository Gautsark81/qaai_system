# qaai_system/__init__.py
"""
Package initializer for qaai_system.

This file intentionally keeps a minimal, safe runtime import behavior:
- applies optional compatibility patches if a 'patch_orchestrator.py' file
  is present in the filesystem (used only during local development).
"""
from __future__ import annotations

import importlib
import importlib.util
import os
import sys
import logging

logger = logging.getLogger("qaai_system")

# Try package-style import first (when installed), else load local patch file if present.
try:
    # Prefer the package import if available
    import qaai_system.patch_orchestrator  # noqa: F401
except Exception:
    try:
        # Fallback: if there is a development patch file at project root, load it
        patch_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "patch_orchestrator.py"))
        if os.path.exists(patch_path):
            spec = importlib.util.spec_from_file_location("qaai_system.patch_orchestrator", patch_path)
            if spec and spec.loader:
                mod = importlib.util.module_from_spec(spec)
                sys.modules["qaai_system.patch_orchestrator"] = mod
                spec.loader.exec_module(mod)
    except Exception:
        logger.exception("Failed to import local patch_orchestrator (non-fatal).")
