from dataclasses import dataclass, field
from typing import Any, Dict, Optional
import os
from dotenv import load_dotenv
import json

load_dotenv()

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
    cfg = {}
    schema = schema or {}
    for key, meta in schema.items():
        if isinstance(meta, dict) and "default" in meta:
            cfg[key] = meta["default"]
        elif not isinstance(meta, dict):
            cfg[key] = meta

    for key in set(list(schema.keys()) + list(os.environ.keys())):
        if key in os.environ:
            raw = os.environ[key]
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

    missing = [k for k, v in (schema.items()) if isinstance(v, dict) and v.get("required") and k not in cfg]
    if missing:
        raise RuntimeError(f"Missing required config keys: {missing}")

    return Config(cfg)

DEFAULT_SCHEMA = {
    "ENV": {"default": "development"},
    "LOG_LEVEL": {"default": "INFO"},
    "LOG_CAPTURE_STDOUT": {"default": "true"},
    "SCHEDULER_MAX_WORKERS": {"default": 10, "type": int},
    "QUEUE_PERSIST_PATH": {"default": ""},
}

def load_default_config() -> Config:
    return load_config(DEFAULT_SCHEMA)
