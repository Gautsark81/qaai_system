from __future__ import annotations

import hashlib
from dataclasses import dataclass
from decimal import Decimal
from typing import Dict, Tuple, Any


# ---------------------------------------------------------------------
# Models
# ---------------------------------------------------------------------


@dataclass(frozen=True)
class PromotionScoreComponent:
    name: str
    value: Decimal
    weight: Decimal
    weighted_score: Decimal


@dataclass(frozen=True)
class PromotionIntelligenceArtifact:
    strategy_dna: str
    total_score: Decimal
    components: Tuple[PromotionScoreComponent, ...]
    state_hash: str


@dataclass(frozen=True)
class PromotionIntelligenceTrace:
    artifact: PromotionIntelligenceArtifact
    trace_hash: str


@dataclass(frozen=True)
class PromotionIntelligenceDecision:
    """
    C6.3 requires evaluate() to return a decision object
    containing a trace attribute.
    """

    trace: PromotionIntelligenceTrace


# ---------------------------------------------------------------------
# Intelligence Engine
# ---------------------------------------------------------------------


class PromotionIntelligenceEngine:

    DEFAULT_WEIGHTS: Dict[str, Decimal] = {
        "ssr_strength": Decimal("0.4"),
        "regime_alignment": Decimal("0.2"),
        "capital_fit": Decimal("0.2"),
        "governance_health": Decimal("0.2"),
    }

    # ------------------------------------------------------------------
    # Core scoring
    # ------------------------------------------------------------------

    def score(
        self,
        *,
        strategy_dna: str,
        ssr_strength: Decimal,
        regime_alignment: Decimal,
        capital_fit: Decimal,
        governance_health: Decimal,
        weights: Dict[str, Decimal] | None = None,
    ) -> PromotionIntelligenceArtifact:

        weights = weights or self.DEFAULT_WEIGHTS

        components = []
        total = Decimal("0")

        inputs = {
            "ssr_strength": ssr_strength,
            "regime_alignment": regime_alignment,
            "capital_fit": capital_fit,
            "governance_health": governance_health,
        }

        for name, value in inputs.items():
            weight = weights[name]
            weighted_score = (Decimal(value) * weight).quantize(Decimal("0.0001"))

            component = PromotionScoreComponent(
                name=name,
                value=Decimal(value),
                weight=weight,
                weighted_score=weighted_score,
            )

            components.append(component)
            total += weighted_score

        total = total.quantize(Decimal("0.0001"))

        state_hash = self._compute_artifact_hash(
            strategy_dna=strategy_dna,
            total=total,
            components=tuple(components),
        )

        return PromotionIntelligenceArtifact(
            strategy_dna=strategy_dna,
            total_score=total,
            components=tuple(components),
            state_hash=state_hash,
        )

    # ------------------------------------------------------------------
    # Snapshot evaluation (Replay-safe)
    # ------------------------------------------------------------------

    def evaluate(
        self,
        *,
        strategy_snapshot: Any,
        capital_snapshot: Any,
        screening_snapshot: Any,
        governance_snapshot: Any,
    ) -> PromotionIntelligenceDecision:

        strategy_dna = self._extract_strategy_dna(strategy_snapshot)

        ssr_strength = self._extract_decimal(
            strategy_snapshot, ("ssr_strength", "ssr", "strength")
        )

        regime_alignment = self._extract_decimal(
            screening_snapshot, ("regime_alignment", "alignment", "regime_score")
        )

        capital_fit = self._extract_decimal(
            capital_snapshot, ("capital_fit", "fit", "capital_score")
        )

        governance_health = self._extract_decimal(
            governance_snapshot, ("governance_health", "health", "governance_score")
        )

        artifact = self.score(
            strategy_dna=strategy_dna,
            ssr_strength=ssr_strength,
            regime_alignment=regime_alignment,
            capital_fit=capital_fit,
            governance_health=governance_health,
        )

        trace_hash = self._compute_trace_hash(artifact)

        trace = PromotionIntelligenceTrace(
            artifact=artifact,
            trace_hash=trace_hash,
        )

        return PromotionIntelligenceDecision(trace=trace)

    # ------------------------------------------------------------------
    # Helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _extract_strategy_dna(snapshot: Any) -> str:
        for attr in ("strategy_dna", "dna", "strategy_id"):
            if hasattr(snapshot, attr):
                return str(getattr(snapshot, attr))
        return str(snapshot)

    @staticmethod
    def _extract_decimal(snapshot: Any, candidates: Tuple[str, ...]) -> Decimal:
        for attr in candidates:
            if hasattr(snapshot, attr):
                return Decimal(str(getattr(snapshot, attr)))
        return Decimal("0")

    # ------------------------------------------------------------------
    # Hashing
    # ------------------------------------------------------------------

    @staticmethod
    def _compute_artifact_hash(
        *,
        strategy_dna: str,
        total: Decimal,
        components: Tuple[PromotionScoreComponent, ...],
    ) -> str:

        base = f"{strategy_dna}|{total}|"

        for c in sorted(components, key=lambda x: x.name):
            base += f"{c.name}:{c.value}:{c.weight}:{c.weighted_score}|"

        return hashlib.sha256(base.encode()).hexdigest()

    @staticmethod
    def _compute_trace_hash(
        artifact: PromotionIntelligenceArtifact,
    ) -> str:

        base = f"{artifact.strategy_dna}|{artifact.state_hash}|{artifact.total_score}"
        return hashlib.sha256(base.encode()).hexdigest()


# Backward compatibility alias required by tests
PromotionIntelligence = PromotionIntelligenceEngine