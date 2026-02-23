# tests/unit/test_config_loader.py
import os
import tempfile
from config.config_loader import load_config, load_default_config, Config

def test_load_default_config():
    cfg = load_default_config()
    assert isinstance(cfg, Config)
    assert "ENV" in cfg

def test_load_config_with_schema_and_env(monkeypatch):
    monkeypatch.setenv("HOST", "example.com")
    schema = {
        "HOST": {"default": "localhost", "required": True},
        "PORT": {"default": 8080, "type": int}
    }
    cfg = load_config(schema)
    assert cfg.get("HOST") == "example.com"
    assert cfg.get("PORT") == 8080
