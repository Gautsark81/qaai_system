from statistics import mean, pstdev
from typing import Sequence

from dashboard.domain.system_mood_drift import (
    SystemMoodSample,
    SystemMoodDriftResult,
)


def compute_system_mood_drift(
    samples: Sequence[SystemMoodSample],
) -> SystemMoodDriftResult:
    if not samples:
        return SystemMoodDriftResult(
            window_size=0,
            samples=(),
            mean=0.0,
            slope=0.0,
            volatility=0.0,
            is_degrading=False,
            explanation="No mood history available.",
        )

    moods = [s.mood for s in samples]
    n = len(moods)

    # Linear regression slope (x = index)
    x = list(range(n))
    x_mean = mean(x)
    y_mean = mean(moods)

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, moods))
    denominator = sum((xi - x_mean) ** 2 for xi in x) or 1.0

    slope = numerator / denominator
    volatility = pstdev(moods)

    is_degrading = slope < 0

    explanation = (
        f"System mood trending {'down' if is_degrading else 'up or stable'} "
        f"over last {n} snapshots "
        f"(slope={slope:.3f}, volatility={volatility:.3f})."
    )

    return SystemMoodDriftResult(
        window_size=n,
        samples=tuple(samples),
        mean=y_mean,
        slope=slope,
        volatility=volatility,
        is_degrading=is_degrading,
        explanation=explanation,
    )
