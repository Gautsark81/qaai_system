# screening/__init__.py

# -------------------------------------------------
# Canonical contracts (must load first)
# -------------------------------------------------
from screening.result import ScreeningResult

# -------------------------------------------------
# Lazy engine accessor (prevents circular imports)
# -------------------------------------------------
def ScreeningEngine(*args, **kwargs):
    from core.screening.engine import ScreeningEngine as _Engine
    return _Engine(*args, **kwargs)


__all__ = [
    "ScreeningResult",
    "ScreeningEngine",
]
