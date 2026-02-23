"""
Compatibility package shim.

Allows legacy imports:
    import operator_dashboard.*
while actual code lives in:
    modules.operator_dashboard.*
"""

# ------------------------------------------------------------
# DO NOT leak built-ins into module namespace
# ------------------------------------------------------------
import types
from pathlib import Path

# ------------------------------------------------------------
# Create alias package object
# ------------------------------------------------------------
_alias_pkg = types.ModuleType("operator_dashboard")
_alias_pkg.__file__ = str(Path(__file__).resolve())
_alias_pkg.__path__ = [str(Path(__file__).parent.resolve())]

# ------------------------------------------------------------
# Import real dashboard modules (ONLY these)
# ------------------------------------------------------------
from modules.operator_dashboard import state_assembler
from modules.operator_dashboard import data_contracts

# ------------------------------------------------------------
# Attach allowed modules ONLY
# ------------------------------------------------------------
_alias_pkg.state_assembler = state_assembler
_alias_pkg.data_contracts = data_contracts

_alias_pkg.__all__ = [
    "state_assembler",
    "data_contracts",
]

# ------------------------------------------------------------
# Register alias WITHOUT polluting namespace
# ------------------------------------------------------------
def _register():
    import sys as _sys  # local import ONLY
    _sys.modules["operator_dashboard"] = _alias_pkg
    _sys.modules["operator_dashboard.state_assembler"] = state_assembler
    _sys.modules["operator_dashboard.data_contracts"] = data_contracts


_register()

# ------------------------------------------------------------
# HARD CLEANUP — ensure no built-ins survive
# ------------------------------------------------------------
del _register
del types
del Path
del state_assembler
del data_contracts
del _alias_pkg
