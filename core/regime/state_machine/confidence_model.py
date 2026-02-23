def compute_confidence_score(
    stability_score: float,
    duration_cycles: int,
    structural_break_score: float,
) -> float:
    duration_weight = min(1.0, duration_cycles / 20.0)

    confidence = (
        0.4 * stability_score +
        0.3 * duration_weight +
        0.3 * (1.0 - structural_break_score)
    )

    return round(min(1.0, max(0.0, confidence)), 6)