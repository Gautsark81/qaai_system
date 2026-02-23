# scripts/run_daily_ingest.py
import argparse
from pathlib import Path
from modules.data_pipeline.fetchers import DummyFetcher
from modules.data_pipeline.ingest import ingest_universe
import yaml
import sys

def load_symbols_from_file(path: Path):
    return [l.strip() for l in path.read_text().splitlines() if l.strip() and not l.strip().startswith("#")]

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--symbols-file", type=Path, help="File with symbols (one per line)", required=False)
    p.add_argument("--symbols", type=str, help="Comma-separated symbols (overrides file)", required=False)
    p.add_argument("--start", type=str, help="Start date YYYY-MM-DD", required=True)
    p.add_argument("--end", type=str, help="End date YYYY-MM-DD", required=True)
    p.add_argument("--out", type=Path, default=Path("data"), required=False)
    p.add_argument("--parallel", type=int, default=4)
    args = p.parse_args()

    if args.symbols:
        symbols = [s.strip() for s in args.symbols.split(",") if s.strip()]
    elif args.symbols_file:
        symbols = load_symbols_from_file(args.symbols_file)
    else:
        print("Provide --symbols or --symbols-file", file=sys.stderr)
        return 2

    fetcher = DummyFetcher()
    out = Path(args.out)
    results = ingest_universe(fetcher, symbols, args.start, args.end, out, parallel=args.parallel)
    # print summary
    for r in results:
        if "error" in r:
            print(f"ERR {r['symbol']}: {r['error']}")
        else:
            print(f"OK  {r['symbol']}: rows={r['rows']} features={r['features_path']}")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
