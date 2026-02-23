"""
Thin wrapper: re-exports the main ScreeningEngineSupercharged from supercharged_engine
to keep backward compatibility.
"""

from qaai_system.screener.supercharged_engine import ScreeningEngineSupercharged

ScreeningEngine = ScreeningEngineSupercharged  # ✅ backward-compatible alias

__all__ = ["ScreeningEngine"]
