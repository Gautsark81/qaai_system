from typing import List, Dict
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed
import traceback
import pandas as pd

from .fetchers import AbstractFetcher
from .store import write_raw_ohlcv, write_features
from .features import compute_rolling_features

def ingest_symbol(fetcher: AbstractFetcher, symbol: str, start: str, end: str, out_dir: Path) -> Dict:
    try:
        df = fetcher.fetch_ohlcv(symbol, start, end)
        if not isinstance(df, pd.DataFrame):
            raise RuntimeError("fetch_ohlcv must return a DataFrame")
        raw_path = write_raw_ohlcv(symbol, df, out_dir)
        features_df = compute_rolling_features(df)
        features_path = write_features(symbol, features_df, out_dir)
        return {"symbol": symbol, "raw_path": str(raw_path), "features_path": str(features_path), "rows": len(df)}
    except Exception as exc:
        return {"symbol": symbol, "error": str(exc), "trace": traceback.format_exc()}

def ingest_universe(fetcher: AbstractFetcher, symbols: List[str], start: str, end: str, out_dir: Path, parallel: int = 4) -> List[Dict]:
    out_dir = Path(out_dir)
    results = []
    if parallel <= 1 or len(symbols) <= 1:
        for s in symbols:
            results.append(ingest_symbol(fetcher, s, start, end, out_dir))
        return results
    with ThreadPoolExecutor(max_workers=parallel) as ex:
        futures = {ex.submit(ingest_symbol, fetcher, s, start, end, out_dir): s for s in symbols}
        for fut in as_completed(futures):
            try:
                results.append(fut.result())
            except Exception as exc:
                results.append({"symbol": futures[fut], "error": str(exc)})
    return results
