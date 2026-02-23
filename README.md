# QAAI Phase 1: Data + Infra Setup

## Steps
1. Clone this repo
2. Ensure `infra/config.yaml` has API keys, paths
3. Install requirements: `pip install -r requirements.txt`
4. Run tests: `pytest tests/`
5. Inspect logs in `/logs/`

## Output Files
- `logs/system.log`
- `output/clean_data.csv`

## What This Phase Covers
- Live + fallback data ingestion
- Schema validation
- Data cleaning
- YAML config loading
- Global logging
- Health check routine

## Migration Guide: BracketManager API

The `BracketManager` provides both a **modern API** and a **legacy API**.
New code should prefer the modern API. The legacy API is kept only for
backward compatibility with older test suites.

---

### 1. Registering Brackets

**Legacy:**
```python
mgr.register(symbol="AAPL", qty=10, entry_price=100.0,
             take_profit=110.0, stop_loss=95.0)

mgr.register_bracket(
    parent_order_id="ORDER123",
    symbol="AAPL",
    side="buy",
    qty=10,
    entry_price=100.0,
    bracket_cfg={
        "take_profits": [{"price": 110.0, "qty_frac": 1.0}],
        "stop": {"price": 95.0}
    }
)

mgr.on_fill({"symbol": "AAPL", "side": "buy", "quantity": 10, "price": 100.0}, router)


# After the parent order fills, explicitly submit bracket orders:
bracket_id = mgr.register_bracket(...)
mgr._submit_bracket_orders(mgr._by_id[bracket_id], router)


mgr.on_tick("AAPL", 102.0, router)


mgr.on_price_tick("AAPL", 102.0, router=router)


mgr.on_fill({"symbol": "AAPL", "side": "sell", "quantity": 10, "price": 110.0}, router)


mgr.on_child_fill(order_id="bracket:tp:1234:110.0",
                  fill={"symbol": "AAPL", "side": "sell", "quantity": 10, "price": 110.0},
                  router=router)


state = mgr.save_state()
mgr.load_state(state)



---

This way you explain:

- What the **new API** looks like.  
- How to translate old method calls.  
- Where persistence is expected to live in the new design.  

---

👉 Do you want me to **inline this migration guide into the top-level docstring of `bracket_manager.py`** so it’s visible to developers in the code, or keep it **only in README.md**?




## BracketManager API

`BracketManager` supports **two styles of API**:

### 🆕 Modern API (preferred)
- `register_bracket(...)` → full-featured config (multi-tier TPs, trailing stops, ATR).
- `on_price_tick(symbol, price, atr=None, router=None)` → update trailing stops, trigger SL/TP.
- `on_child_fill(order_id, fill, router=None)` → handle child TP/SL fills directly.

### 🧩 Legacy API (for backward-compatibility & tests)
- `register(...)` → shorthand for single TP/SL with optional trailing.
- `on_fill(fill, router=None)` → entrypoint for parent order fill or child order fill (auto-detects).
- `on_tick(symbol, price, router=None, atr=None)` → alias for `on_price_tick`.
- `save_state()` / `load_state(state)` → simplified persistence (symbol → TP/SL view).

Legacy methods are **thin wrappers** over the modern API.  
They exist to keep older test suites and integrations working while encouraging migration to the newer, more expressive API.

## Export helpers
- `safe_to_ist(series)` converts datetimes to timezone-naive IST (Asia/Kolkata) for Excel.
- `export_df_to_excel(df, path, sheet_name=...)` writes atomically (temp .xlsx + os.replace).

# Build image
docker-compose build

# Run services (in background)
docker-compose up -d

# View logs
docker-compose logs -f app

# Open metrics
http://localhost:8000/  # Prometheus metrics endpoint

Supercharged Backtester v1
-------------------------
# run tests
pytest tests/test_supercharged_backtester.py -q

# quick usage example
python -c "from backtester.supercharged_backtester import SuperchargedBacktester; print('ok')"

Live Tick Streaming Microservice
-------------------------------
# using dhanhq SDK:
pip install dhanhq  # or install from repo
python services/live_tick_service.py --client-id YOUR_CLIENT_ID --access-token YOUR_TOKEN

# with redis (optional):
docker run -d --name amats-redis -p 6379:6379 redis:7-alpine
python services/live_tick_service.py --client-id ... --access-token ... --use-redis

