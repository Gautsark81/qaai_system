# tools/replay_live_feed.py
from __future__ import annotations
import ast
import time
import sys
from pathlib import Path
from data.tick_store import TickStore

def normalize_packet(pkt):
    # same logic as services/live_tick_service.normalize_packet, simplified
    pkt_type = pkt.get("type", "").lower()
    sec_id = pkt.get("security_id")
    symbol = str(sec_id)
    if "LTP" in pkt:
        try:
            price = float(pkt.get("LTP"))
        except Exception:
            price = None
    elif "ltp" in pkt:
        price = float(pkt.get("ltp"))
    else:
        price = None
    size = int(pkt.get("LTQ", pkt.get("ltq", pkt.get("size", 0))))
    ts = pkt.get("timestamp") or pkt.get("ts") or None
    if ts is None:
        LTT = pkt.get("LTT")
        if LTT:
            try:
                today = time.strftime("%Y-%m-%d")
                dt = f"{today} {LTT}"
                ts = time.mktime(time.strptime(dt, "%Y-%m-%d %H:%M:%S"))
            except Exception:
                ts = time.time()
        else:
            ts = time.time()
    try:
        ts = float(ts)
    except Exception:
        ts = time.time()
    if price is None:
        return None
    return {
        "symbol": symbol,
        "timestamp": ts,
        "price": price,
        "size": int(size or 0),
        "raw_type": pkt.get("type"),
        "raw_json": pkt,
    }

def replay_file(path, tick_store):
    tcount = 0
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            # try to parse as Python dict literal
            try:
                pkt = ast.literal_eval(line)
            except Exception:
                # try to strip trailing commas or other artifacts
                try:
                    pkt = ast.literal_eval(line.rstrip(","))
                except Exception:
                    # fallback: skip
                    continue
            tick = normalize_packet(pkt)
            if tick:
                tick_store.append_tick(tick["symbol"], tick)
                tcount += 1
    return tcount

def main():
    if len(sys.argv) < 2:
        print("Usage: python tools/replay_live_feed.py PATH_TO_LOG [DB_PATH]")
        sys.exit(1)
    path = Path(sys.argv[1])
    if not path.exists():
        print("File not found:", path)
        sys.exit(2)
    db = ":memory:"
    if len(sys.argv) >= 3:
        db = sys.argv[2]
    ts = TickStore(db_path=db)
    n = replay_file(str(path), ts)
    print(f"Imported {n} ticks into TickStore ({db})")
    # optionally print snapshot
    try:
        sample = ts.get_ticks(next(iter(ts.get_symbols())), limit=5)
        print("Sample ticks:", sample)
    except Exception:
        pass
    ts.close()

if __name__ == "__main__":
    main()
