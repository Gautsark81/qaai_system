# tools/normalize_trades.py
import json
from pathlib import Path
from datetime import datetime

REQ_FIELDS = [
    "strategy_id",
    "version",
    "run_mode",
    "symbol",
    "order_id",
    "entry_ts",
    "exit_ts",
    "entry_price",
    "exit_price",
    "qty",
    "side",
    "pnl",
    "holding_period_minutes",
    "sl_hit",
    "tp_hit",
    "fees",
    # many analytics functions also expect a trade_date column
    "trade_date",
]

DATADIR = Path("data/trades")
if not DATADIR.exists():
    print("No data/trades folder found.")
    raise SystemExit(1)

for f in sorted(DATADIR.glob("*.jsonl")):
    outp = f.with_name(f.stem + "_normalized.jsonl")
    count_in = 0
    count_out = 0
    with f.open("r", encoding="utf-8") as inf, outp.open("w", encoding="utf-8") as outf:
        for line in inf:
            count_in += 1
            try:
                r = json.loads(line)
            except Exception:
                continue
            # ensure fields
            # strategy_id
            if "strategy_id" not in r or not r.get("strategy_id"):
                r["strategy_id"] = r.get("meta", {}).get("strategy_id", "paper_sim")
            if "version" not in r or not r.get("version"):
                r["version"] = r.get("meta", {}).get("version", "paper")
            if "run_mode" not in r:
                r["run_mode"] = "paper"
            if "symbol" not in r or not r.get("symbol"):
                r["symbol"] = r.get("meta", {}).get("symbol", r.get("symbol", "MOCK"))
            # times
            if "entry_ts" not in r or not r.get("entry_ts"):
                r["entry_ts"] = datetime.utcnow().isoformat()
            if "exit_ts" not in r:
                r["exit_ts"] = None
            # trade_date
            try:
                r["trade_date"] = r.get("entry_ts", "")[:10]
            except Exception:
                r["trade_date"] = datetime.utcnow().strftime("%Y-%m-%d")
            # minimal numeric fields
            r["entry_price"] = float(r.get("entry_price", r.get("entry_price", r.get("execution_price", 0.0) or 0.0) or 0.0))
            r["exit_price"] = float(r.get("exit_price", r.get("exit_price", 0.0) or 0.0))
            r["qty"] = int(r.get("qty", r.get("quantity", r.get("position_size", 1))))
            r["side"] = r.get("side", "BUY")
            r["pnl"] = float(r.get("pnl", 0.0))
            r["holding_period_minutes"] = int(r.get("holding_period_minutes", r.get("holding_period", 0) or 0))
            r["sl_hit"] = bool(r.get("sl_hit", False))
            r["tp_hit"] = bool(r.get("tp_hit", False))
            r["fees"] = float(r.get("fees", 0.0))
            # write normalized JSONL
            outf.write(json.dumps(r) + "\n")
            count_out += 1
    print(f"Wrote {outp} ({count_out}/{count_in} records normalized)")
print("Normalization complete. You may delete original files after inspection.")
