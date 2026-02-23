"""
Alpha Decay Analysis Module.

This package provides:
- Immutable decay diagnostics (DecaySnapshot)
- Canonical decay state classification (AlphaDecayState)
- Deterministic decay detector (AlphaDecayDetector)

Design principles:
- Stateless
- Deterministic
- Governance-first
- Engine-agnostic
"""

from .model import (
    DecaySnapshot,
    AlphaDecayState,
    AlphaDecayDetector,
)

__all__ = [
    "DecaySnapshot",
    "AlphaDecayState",
    "AlphaDecayDetector",
]
