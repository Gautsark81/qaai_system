"""
Robust config loader.
- Loads .env via python-dotenv if present
- Loads environment variables
- Supports defaults and simple validators
- Returns a dict-like Config object
"""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
import json

load_dotenv()  # loads .env into environment if present


@dataclass
class Config:
    _values: Dict[str, Any] = field(default_factory=dict)

    def get(self, key: str, default: Optional[Any] = None) -> Any:
        return self._values.get(key, default)

    def __getitem__(self, key: str) -> Any:
        return self._values[key]

    def __contains__(self, key: str) -> bool:
        return key in self._values

    def as_dict(self) -> Dict[str, Any]:
        return dict(self._values)


def load_config(schema: Optional[Dict[str, Any]] = None) -> Config:
    """
    Load config from environment. Optionally provide a schema dict with
    default values and optional validators:
        schema = {
            "HOST": {"default": "localhost", "required": True},
            "PORT": {"default": 8080, "type": int}
        }
    """
    cfg = {}
    schema = schema or {}
    # First fill defaults
    for key, meta in schema.items():
        if isinstance(meta, dict) and "default" in meta:
            cfg[key] = meta["default"]
        elif not isinstance(meta, dict):
            cfg[key] = meta

    # Override with env vars
    for key in set(list(schema.keys()) + list(os.environ.keys())):
        if key in os.environ:
            raw = os.environ[key]
            # Apply type coercion if schema says so
            meta = schema.get(key)
            if isinstance(meta, dict) and "type" in meta:
                t = meta["type"]
                try:
                    if t is bool:
                        val = raw.lower() in ("1", "true", "yes", "on")
                    else:
                        val = t(raw)
                except Exception:
                    val = raw
            else:
                val = raw
            cfg[key] = val

    # Validate required keys
    missing = [k for k, v in (schema.items()) if isinstance(v, dict) and v.get("required") and k not in cfg]
    if missing:
        raise RuntimeError(f"Missing required config keys: {missing}")

    return Config(cfg)


# Helper: produce a sample schema for Phase-0
DEFAULT_SCHEMA = {
    "ENV": {"default": "development"},
    "LOG_LEVEL": {"default": "INFO"},
    "LOG_CAPTURE_STDOUT": {"default": "true"},
    "SCHEDULER_MAX_WORKERS": {"default": 10, "type": int},
    "QUEUE_PERSIST_PATH": {"default": ""},
}

# convenient loader
def load_default_config() -> Config:
    return load_config(DEFAULT_SCHEMA)


if __name__ == "__main__":
    cfg = load_default_config()
    print("Loaded config:", json.dumps(cfg.as_dict(), indent=2))
