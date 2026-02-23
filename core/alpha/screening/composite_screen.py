# core/alpha/screening/composite_screen.py

from typing import List

from .composite_input import CompositeScreeningInput
from .composite_verdict import CompositeScreeningVerdict


ORDERED_STEPS = [
    "liquidity",
    "regime",
    "statistical_illusion",
    "cross_factor",
    "structural_risk",
    "crowding_risk",
    "tail_risk",
]


def run_composite_screening(
    inputs: CompositeScreeningInput,
) -> CompositeScreeningVerdict:
    for step in ORDERED_STEPS:
        verdict = getattr(inputs, step)

        if verdict.passed is False:
            return CompositeScreeningVerdict(
                passed=False,
                failed_step=step,
                blocked_dimensions=tuple(verdict.blocked_dimensions),
            )

    return CompositeScreeningVerdict(
        passed=True,
        failed_step=None,
        blocked_dimensions=(),
    )
