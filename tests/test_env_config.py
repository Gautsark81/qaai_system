from qaai_system import env_config as cfg


def test_env_config_defaults():
    assert cfg.MODE in ("paper", "live")
    assert isinstance(cfg.TOP_K, int)
    assert cfg.LOG_LEVEL.isupper()
    assert isinstance(cfg.POSTGRES_PORT, int)
    assert cfg.ACCOUNT_EQUITY > 0


def test_ensure_dirs(tmp_path, monkeypatch):
    monkeypatch.setattr(cfg, "LOG_DIR", str(tmp_path / "logs"))
    monkeypatch.setattr(
        cfg, "SIGNALS_PATH", str(tmp_path / "signals/latest_signals.csv")
    )
    monkeypatch.setattr(cfg, "TRADE_LOG_PATH", str(tmp_path / "trades/trade_log.csv"))
    monkeypatch.setattr(cfg, "MARKET_LOG_PATH", str(tmp_path / "market/price_data.csv"))
    monkeypatch.setattr(cfg, "AUDIT_DIR", str(tmp_path / "audit"))

    cfg.ensure_dirs()

    assert (tmp_path / "logs").exists()
    assert (tmp_path / "signals").exists()
    assert (tmp_path / "trades").exists()
    assert (tmp_path / "market").exists()
    assert (tmp_path / "audit").exists()
