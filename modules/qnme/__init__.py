# modules/qnme/__init__.py
"""
Quantum Neural Market Engine (QNME) modules package.
Each module implements one of the 12 QNME layers.

This package contains conservative, well-documented skeletons that are
ready for incremental hardening (vectorization, persistence, ML models).
"""
__all__ = [
    "genome", "regime", "strategy_pool", "gates", "meta_controller",
    "learning", "mutation", "fusion", "macro_intel", "risk", "anomaly",
    "override", "orchestrator"
]
