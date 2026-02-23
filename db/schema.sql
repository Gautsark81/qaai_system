-- db/schema.sql
PRAGMA foreign_keys = OFF;
BEGIN TRANSACTION;

-- OHLCV table
CREATE TABLE IF NOT EXISTS ohlcv (
    ts TEXT NOT NULL,
    symbol TEXT NOT NULL,
    timeframe TEXT NOT NULL DEFAULT '1m',
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume REAL,
    PRIMARY KEY (ts, symbol, timeframe)
);

-- Tick table
CREATE TABLE IF NOT EXISTS ticks (
    ts TEXT NOT NULL,
    symbol TEXT NOT NULL,
    price REAL,
    volume REAL,
    bid REAL,
    ask REAL,
    PRIMARY KEY (ts, symbol)
);

-- Feature table
CREATE TABLE IF NOT EXISTS features (
    ts TEXT NOT NULL,
    symbol TEXT NOT NULL,
    feature_key TEXT NOT NULL,
    feature_value REAL,
    PRIMARY KEY (ts, symbol, feature_key)
);

-- Audit log
CREATE TABLE IF NOT EXISTS audit_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ts TEXT,
    component TEXT,
    level TEXT,
    message TEXT,
    meta_json TEXT
);

-- ML predictions table
CREATE TABLE IF NOT EXISTS ml_predictions (
    ts TEXT,
    order_id TEXT,
    symbol TEXT,
    side TEXT,
    qty REAL,
    price REAL,
    nav REAL,
    last_price REAL,
    p_fill REAL,
    model_version TEXT,
    outcome_status TEXT
);

-- exporter_state for last_export_ts marker
CREATE TABLE IF NOT EXISTS exporter_state (
    k TEXT PRIMARY KEY,
    v TEXT
);

COMMIT;
