# modules/strategy/rule_config.py
from __future__ import annotations
import yaml
from typing import Union, Dict, Any

def load_rule_config(src: Union[str, bytes]) -> Dict[str, Any]:
    """
    src can be a file path or a YAML string. Returns dict for rule engine.
    """
    if isinstance(src, (bytes, str)):
        try:
            # try reading file first
            with open(src, "r", encoding="utf8") as f:
                return yaml.safe_load(f)
        except Exception:
            # fallback: parse as YAML string
            return yaml.safe_load(src)
    raise ValueError("unsupported src type")
