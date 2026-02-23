# core/alpha/screening/__init__.py

from .structural_evidence import StructuralRiskEvidence
from .structural_verdict import StructuralRiskVerdict
from .structural_screen import run_structural_risk_screen
from .crowding_evidence import CrowdingRiskEvidence
from .crowding_verdict import CrowdingRiskVerdict
from .crowding_screen import run_crowding_risk_screen
from .tail_risk_evidence import TailRiskEvidence
from .tail_risk_verdict import TailRiskVerdict
from .tail_risk_screen import run_tail_risk_screen
from .composite_input import CompositeScreeningInput
from .composite_verdict import CompositeScreeningVerdict
from .composite_screen import run_composite_screening



__all__ = [
    "StructuralRiskEvidence",
    "StructuralRiskVerdict",
    "run_structural_risk_screen",
]

# Defensive __all__ initialization (L3-safe)
try:
    __all__
except NameError:
    __all__ = []

__all__ += [
    "CrowdingRiskEvidence",
    "CrowdingRiskVerdict",
    "run_crowding_risk_screen",
]

__all__ += [
    "TailRiskEvidence",
    "TailRiskVerdict",
    "run_tail_risk_screen",
]

__all__ += [
    "CompositeScreeningInput",
    "CompositeScreeningVerdict",
    "run_composite_screening",
]