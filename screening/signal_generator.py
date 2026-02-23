from __future__ import annotations

import uuid
import pandas as pd
from core.screening.pipeline import ScreeningPipeline


def generate_signals(
    df: pd.DataFrame,
    **pipeline_kwargs,
) -> pd.DataFrame:
    """
    Thin wrapper for ScreeningPipeline with contract normalization.

    Guarantees:
    - kwargs passed directly to pipeline constructor
    - run(df) signature
    - 'status' column always present
    - 'signal_id' column always present
    """

    pipeline = ScreeningPipeline(**pipeline_kwargs)
    result = pipeline.run(df)

    # ------------------------------------------------------------------
    # Contract normalization (public API guarantee)
    # ------------------------------------------------------------------
    result = result.copy()

    if "status" not in result.columns:
        # Deterministic default: signal successfully generated
        result["status"] = "generated"

    if "signal_id" not in result.columns:
        # Stable, unique identifier per signal
        result["signal_id"] = [
            f"{row.symbol}-{uuid.uuid4().hex[:8]}"
            for row in result.itertuples(index=False)
        ]

    return result
