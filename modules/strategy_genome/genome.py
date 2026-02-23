from dataclasses import dataclass, field
from typing import Dict, Any, Optional
import hashlib
import json


# ==========================================================
# STRATEGY GENOME
# ==========================================================

@dataclass(frozen=True)
class StrategyGenome:
    """
    Immutable, reproducible definition of a strategy.

    This is the SINGLE SOURCE OF TRUTH for:
    - what the strategy is
    - how it was created
    - how it can be reproduced
    """

    strategy_type: str                     # e.g. "mean_reversion"
    symbol_universe: str                   # e.g. "NSE_ALL"
    timeframe: str                         # e.g. "5m"

    parameters: Dict[str, Any]             # tunable knobs
    features: Dict[str, Any]               # feature definitions

    parent_id: Optional[str] = None        # lineage
    generation: int = 0
    mutation_reason: Optional[str] = None

    seed: int = 0                          # reproducibility seed

    # ------------------------------------------------------
    # IDENTITY
    # ------------------------------------------------------

    def fingerprint(self) -> str:
        """
        Deterministic hash of the genome.
        Changing ANY field changes the identity.
        """

        payload = {
            "strategy_type": self.strategy_type,
            "symbol_universe": self.symbol_universe,
            "timeframe": self.timeframe,
            "parameters": self.parameters,
            "features": self.features,
            "parent_id": self.parent_id,
            "generation": self.generation,
            "mutation_reason": self.mutation_reason,
            "seed": self.seed,
        }

        canonical = json.dumps(payload, sort_keys=True)
        return hashlib.sha256(canonical.encode()).hexdigest()
