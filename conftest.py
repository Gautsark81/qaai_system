"""
Root-level pytest bootstrap for qaai_system.

Purpose:
- Ensure repo root is always on sys.path
- Make flat legacy namespaces importable:
  `screening`, `watchlist`, `pipeline`, `strategies`, etc.
- Must stay minimal and side-effect free
"""

import sys
from pathlib import Path

# Absolute path to repo root (this file lives at repo root)
REPO_ROOT = Path(__file__).resolve().parent

# Insert repo root at highest priority
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))
