# top-level config package shim that exposes the loader API tests expect.
from .config_loader import load_config, load_default_config, Config
__all__ = ["load_config", "load_default_config", "Config"]
