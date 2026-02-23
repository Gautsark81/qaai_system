# path: qaai_system/risk/risk_config.py
from __future__ import annotations

"""
Helpers to load RiskLimits from YAML / JSON profiles.

Typical usage:

    from qaai_system.risk.risk_config import load_risk_profile

    limits = load_risk_profile("live")
"""

import json
import os
from typing import Optional

from qaai_system.risk.risk_limits import RiskLimits

try:
    import yaml  # type: ignore
except Exception:
    yaml = None


def load_risk_limits_from_file(path: str) -> RiskLimits:
    """
    Load RiskLimits from a YAML or JSON file.

    The file should contain keys matching RiskLimits fields. Unknown keys
    are ignored.

    YAML is used if the extension is .yml/.yaml and PyYAML is available.
    Otherwise, JSON is expected.
    """
    if not os.path.exists(path):
        raise FileNotFoundError(path)

    _, ext = os.path.splitext(path)
    ext = ext.lower()

    if ext in {".yaml", ".yml"} and yaml is not None:
        with open(path, "r", encoding="utf-8") as f:
            data = yaml.safe_load(f) or {}
    else:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f) or {}

    # Only keep keys that exist on RiskLimits
    fields = {f.name for f in RiskLimits.__dataclass_fields__.values()}  # type: ignore[attr-defined]
    filtered = {k: v for k, v in data.items() if k in fields}
    return RiskLimits(**filtered)


def load_risk_profile(
    env: str,
    base_dir: str = "config",
    *,
    default: Optional[RiskLimits] = None,
) -> RiskLimits:
    """
    Load a risk profile for the given environment.

    Tries (in order):
        {base_dir}/risk_profile_{env}.yaml
        {base_dir}/risk_profile_{env}.yml
        {base_dir}/risk_profile_{env}.json

    If none exist and `default` is provided, returns default.
    Otherwise raises FileNotFoundError.
    """
    candidates = [
        os.path.join(base_dir, f"risk_profile_{env}.yaml"),
        os.path.join(base_dir, f"risk_profile_{env}.yml"),
        os.path.join(base_dir, f"risk_profile_{env}.json"),
    ]

    for path in candidates:
        if os.path.exists(path):
            return load_risk_limits_from_file(path)

    if default is not None:
        return default

    raise FileNotFoundError(
        f"No risk profile found for env={env} in {base_dir} "
        f"(tried: {', '.join(candidates)})"
    )
