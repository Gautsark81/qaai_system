# tools/generate_synthetic_trades.py
import json, random
from pathlib import Path
from datetime import datetime, timedelta

OUT = Path("data/trades/paper_trades_synth.jsonl")
OUT.parent.mkdir(parents=True, exist_ok=True)

strategies = ["mean_rev_intraday", "breakout_1m", "momentum_day", "fallback"]
symbols = ["NSE:RELIANCE", "NSE:TCS", "NSE:INFY", "NSE:ICICI"]
start_date = datetime.utcnow().date() - timedelta(days=60)  # 60 days history

def rand_trade(sid, ver, symbol, d):
    entry_ts = datetime.combine(d, datetime.min.time()) + timedelta(minutes=random.randint(60, 360))
    holding = random.randint(5, 180)  # minutes
    entry_price = round(random.uniform(100, 2000), 2)
    pnl_move = random.normalvariate(0.0, 0.01) * entry_price
    exit_price = round(entry_price + pnl_move, 2)
    side = random.choice(["BUY", "SELL"])
    qty = random.choice([1, 1, 1, 2, 5])
    pnl = round((exit_price - entry_price) * qty * (1 if side == "BUY" else -1), 2)
    fees = round(abs(pnl) * 0.001, 2)
    trade = {
        "strategy_id": sid,
        "version": ver,
        "run_mode": "paper",
        "symbol": symbol,
        "order_id": f"synth-{sid}-{symbol}-{int(entry_ts.timestamp())}",
        "entry_ts": entry_ts.isoformat(),
        "exit_ts": (entry_ts + timedelta(minutes=holding)).isoformat(),
        "entry_price": entry_price,
        "exit_price": exit_price,
        "qty": qty,
        "side": side,
        "pnl": pnl - fees,
        "holding_period_minutes": holding,
        "sl_hit": False,
        "tp_hit": False,
        "fees": fees,
        "meta": {"strategy_id": sid, "version": ver},
        "trade_date": entry_ts.strftime("%Y-%m-%d"),
    }
    return trade

def generate(n_days=60, per_day=4):
    rows = []
    for d in (start_date + timedelta(days=i) for i in range(n_days)):
        for _ in range(per_day):
            sid = random.choice(strategies)
            ver = "v1"
            sym = random.choice(symbols)
            rows.append(rand_trade(sid, ver, sym, d))
    return rows

if __name__ == "__main__":
    rows = generate(n_days=30, per_day=6)  # 30*6 = 180 trades by default
    with OUT.open("a", encoding="utf-8") as f:
        for r in rows:
            f.write(json.dumps(r) + "\n")
    print(f"Wrote {len(rows)} synthetic trades to {OUT}")
