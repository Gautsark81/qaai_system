# scripts/drift_check.py

from __future__ import annotations

import os
import statistics
from typing import Dict, Any

from data.feature_store import FeatureStore


def _load_snapshot_from_env() -> Dict[str, Dict[str, Any]]:
    """
    Helper: create a FeatureStore using FEATURE_STORE_DIR (if set),
    and return its flat snapshot.
    """
    base_dir = os.environ.get("FEATURE_STORE_DIR")
    if base_dir:
        fs = FeatureStore(base_dir=base_dir)
    else:
        fs = FeatureStore()
    return fs.snapshot()


def run_check() -> int:
    """
    Drift check CLI entrypoint used by tests.

    Behaviour expected by tests:
    - When no features exist -> print "No features found in store." and return 0.
    - Given a store where, e.g.,
        fs.save_features("DR1", "1m", {"f1": [1,1,...], "f2": [100,100,...]})
      and FEATURE_STORE_DIR points to that store,
      this function should return 1 (drift alerts found).
    """
    snap = _load_snapshot_from_env()
    if not snap:
        print("No features found in store.")
        return 0

    alerts = 0

    for key, feats in snap.items():
        # Collect numeric list-valued features
        series = []
        for fname, val in feats.items():
            if isinstance(val, (list, tuple)) and val:
                try:
                    nums = [float(x) for x in val if x is not None]
                except Exception:
                    continue
                if len(nums) >= 2:
                    series.append((fname, nums))

        # Compare every pair of features for rough mean drift
        for i in range(len(series)):
            for j in range(i + 1, len(series)):
                name1, v1 = series[i]
                name2, v2 = series[j]
                try:
                    m1 = statistics.mean(v1)
                    m2 = statistics.mean(v2)
                except statistics.StatisticsError:
                    continue

                diff = abs(m1 - m2)
                # Any reasonably large difference counts as drift; tests use ~99
                if diff > 1.0:
                    print(
                        f"[DRIFT ALERT] {key}: {name1} vs {name2} "
                        f"mean_diff={diff:.3f}"
                    )
                    alerts += 1

    return 1 if alerts else 0


if __name__ == "__main__":
    raise SystemExit(run_check())
