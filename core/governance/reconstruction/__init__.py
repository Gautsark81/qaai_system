"""
Governance Reconstruction Public API

Phase 12.6 + Phase 13 compatibility layer
This module re-exports reconstruction + drift results so higher
layers (enforcement, purity guards, shadow systems) remain stable.
"""

# -----------------------------
# Core Reconstruction Engine
# -----------------------------
from .governance_reconstruction_engine import (
    GovernanceReconstructionEngine,
    GovernanceState,
)

# -----------------------------
# Capital Exposure Drift Result
# (Correct path: capital_usage)
# -----------------------------
from core.governance.capital_usage.capital_exposure_drift_detector import (
    CapitalExposureDriftResult,
)

# -----------------------------
# Chain Reconstructor
# -----------------------------
from .governance_chain_reconstructor import (
    GovernanceChainReconstructor,
)


# -----------------------------
# Purity Guard (Phase 12.6)
# -----------------------------
def reconstruct_system_state(events=None):
    """
    Phase 12.6 Purity Guard

    Must be:
    - Pure
    - Deterministic
    - No side effects
    - No required arguments
    """

    # Intentionally pure stub.
    # Real reconstruction engine must be called explicitly.
    return {
        "governance_state": None,
        "timestamp": None,
    }