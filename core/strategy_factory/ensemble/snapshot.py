import hashlib
import json
from dataclasses import dataclass, field
from typing import List, Dict
from .models import EnsembleStrategy


@dataclass(frozen=True)
class EnsembleSnapshot:
    strategies: List[EnsembleStrategy]
    available_capital: float
    global_cap: float
    per_strategy_cap: float
    concentration_cap: float

    # ---------------- Suspension thresholds ----------------
    suspension_drawdown_pct: float = 30.0
    suspension_min_ssr: float = 80.0

    # ---------------- Adaptive Meta Weights ----------------
    meta_ssr_weight: float = 0.30
    meta_drawdown_weight: float = 0.25
    meta_capital_eff_weight: float = 0.20
    meta_governance_weight: float = 0.15
    meta_concentration_weight: float = 0.10

    # ---------------- ML Controls ----------------
    meta_ml_enabled: bool = False
    meta_ml_max_total_drift_pct: float = 0.05
    meta_ml_max_single_drift_pct: float = 0.03
    meta_ml_min_return_delta: float = 0.002
    meta_ml_max_drawdown_delta: float = 0.001
    meta_ml_required_shadow_cycles: int = 20

    # ---------------- Diversity + Decay ----------------
    diversity_penalty_strength: float = 0.30
    decay_penalty_strength: float = 0.30

    # ---------------- Reinforcement ----------------
    reinforcement_strength: float = 0.10  # 0–1 bounded

    # ---------------- Strategy Retirement Governance ----------------
    retirement_enabled: bool = True
    retirement_min_ssr: float = 75.0
    retirement_decay_threshold: float = 0.60  # 0–1 bounded

    # ---------------- C15 Regime Adaptation ----------------
    regime_score: float = 0.0  # -1.0 to +1.0
    regime_decay_multiplier: float = 0.50
    regime_reinforcement_multiplier: float = 0.50

    # ---------------- C15.3 Regime Stability Filter ----------------
    previous_regime_score: float = 0.0
    regime_max_step: float = 0.25
    regime_smoothing_alpha: float = 0.5

    # ---------------- Deterministic Decay Scores ----------------
    decay_scores: Dict[str, float] = field(default_factory=dict)

    snapshot_hash: str = field(init=False)

    # ==========================================================
    # Initialization
    # ==========================================================
    def __post_init__(self):
        self._validate_meta_weights()
        self._validate_ml_governance()
        self._validate_diversity_penalty()
        self._validate_decay_penalty()
        self._validate_reinforcement()
        self._validate_retirement()
        self._validate_regime()
        self._validate_regime_stability()
        self._validate_decay_scores()
        object.__setattr__(self, "snapshot_hash", self._compute_hash())

    # ==========================================================
    # Validators
    # ==========================================================

    def _validate_meta_weights(self):
        weights = [
            self.meta_ssr_weight,
            self.meta_drawdown_weight,
            self.meta_capital_eff_weight,
            self.meta_governance_weight,
            self.meta_concentration_weight,
        ]
        if not all(0.05 <= w <= 0.50 for w in weights):
            raise ValueError("Meta weights must be between 0.05 and 0.50")
        if abs(sum(weights) - 1.0) > 1e-6:
            raise ValueError("Meta weights must sum to 1.0")

    def _validate_ml_governance(self):
        if self.meta_ml_required_shadow_cycles < 1:
            raise ValueError("Required shadow cycles must be >= 1")
        if self.meta_ml_max_total_drift_pct < 0:
            raise ValueError("Total drift threshold must be non-negative")
        if self.meta_ml_max_single_drift_pct < 0:
            raise ValueError("Single drift threshold must be non-negative")

    def _validate_diversity_penalty(self):
        if not (0.0 <= self.diversity_penalty_strength <= 1.0):
            raise ValueError("diversity_penalty_strength must be between 0 and 1")

    def _validate_decay_penalty(self):
        if not (0.0 <= self.decay_penalty_strength <= 1.0):
            raise ValueError("decay_penalty_strength must be between 0 and 1")

    def _validate_reinforcement(self):
        if not (0.0 <= self.reinforcement_strength <= 1.0):
            raise ValueError("reinforcement_strength must be between 0 and 1")

    def _validate_retirement(self):
        if not (0.0 <= self.retirement_decay_threshold <= 1.0):
            raise ValueError("retirement_decay_threshold must be between 0 and 1")
        if self.retirement_min_ssr < 0:
            raise ValueError("retirement_min_ssr must be non-negative")

    def _validate_regime(self):
        if not (-1.0 <= self.regime_score <= 1.0):
            raise ValueError("regime_score must be between -1.0 and 1.0")
        if not (0.0 <= self.regime_decay_multiplier <= 1.0):
            raise ValueError("regime_decay_multiplier must be between 0 and 1")
        if not (0.0 <= self.regime_reinforcement_multiplier <= 1.0):
            raise ValueError("regime_reinforcement_multiplier must be between 0 and 1")

    def _validate_regime_stability(self):
        if not (-1.0 <= self.previous_regime_score <= 1.0):
            raise ValueError("previous_regime_score must be between -1.0 and 1.0")
        if not (0.0 <= self.regime_max_step <= 1.0):
            raise ValueError("regime_max_step must be between 0 and 1")
        if not (0.0 <= self.regime_smoothing_alpha <= 1.0):
            raise ValueError("regime_smoothing_alpha must be between 0 and 1")

    def _validate_decay_scores(self):
        for sid, score in self.decay_scores.items():
            if not (0.0 <= score <= 1.0):
                raise ValueError(f"Decay score for {sid} must be between 0 and 1")

    # ==========================================================
    # Deterministic Snapshot Hash
    # ==========================================================
    def _compute_hash(self) -> str:
        payload = {
            "strategies": [
                {
                    "strategy_id": s.strategy_id,
                    "ssr": s.ssr,
                    "drawdown_pct": s.drawdown_pct,
                }
                for s in self.strategies
            ],
            "available_capital": self.available_capital,
            "global_cap": self.global_cap,
            "per_strategy_cap": self.per_strategy_cap,
            "concentration_cap": self.concentration_cap,
            "suspension_drawdown_pct": self.suspension_drawdown_pct,
            "suspension_min_ssr": self.suspension_min_ssr,
            "meta_ssr_weight": self.meta_ssr_weight,
            "meta_drawdown_weight": self.meta_drawdown_weight,
            "meta_capital_eff_weight": self.meta_capital_eff_weight,
            "meta_governance_weight": self.meta_governance_weight,
            "meta_concentration_weight": self.meta_concentration_weight,
            "meta_ml_enabled": self.meta_ml_enabled,
            "meta_ml_max_total_drift_pct": self.meta_ml_max_total_drift_pct,
            "meta_ml_max_single_drift_pct": self.meta_ml_max_single_drift_pct,
            "meta_ml_min_return_delta": self.meta_ml_min_return_delta,
            "meta_ml_max_drawdown_delta": self.meta_ml_max_drawdown_delta,
            "meta_ml_required_shadow_cycles": self.meta_ml_required_shadow_cycles,
            "diversity_penalty_strength": self.diversity_penalty_strength,
            "decay_penalty_strength": self.decay_penalty_strength,
            "reinforcement_strength": self.reinforcement_strength,
            "retirement_enabled": self.retirement_enabled,
            "retirement_min_ssr": self.retirement_min_ssr,
            "retirement_decay_threshold": self.retirement_decay_threshold,
            "regime_score": self.regime_score,
            "regime_decay_multiplier": self.regime_decay_multiplier,
            "regime_reinforcement_multiplier": self.regime_reinforcement_multiplier,
            "previous_regime_score": self.previous_regime_score,
            "regime_max_step": self.regime_max_step,
            "regime_smoothing_alpha": self.regime_smoothing_alpha,
            "decay_scores": dict(sorted(self.decay_scores.items())),
        }

        encoded = json.dumps(payload, sort_keys=True).encode()
        return hashlib.sha256(encoded).hexdigest()