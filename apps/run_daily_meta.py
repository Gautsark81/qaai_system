# path: qaai_system/apps/run_daily_meta.py
from __future__ import annotations

import argparse
import logging
from datetime import date

from data.watchlist_builder import build_daily_universe, save_universe_for_date
from analytics.strategy_metrics import recompute_strategy_metrics
from analytics.promotion_engine import build_daily_run_plan


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(message)s",
    )


def main(argv: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Daily meta pipeline: universe + metrics + run plan."
    )
    parser.add_argument(
        "--date",
        type=str,
        default=None,
        help="ISO date for which to run the pipeline (default: today).",
    )
    parser.add_argument(
        "--mode",
        type=str,
        choices=["paper", "live"],
        default="paper",
        help="Target mode for today's plan (default: paper).",
    )
    args = parser.parse_args(argv)

    configure_logging()
    target_date = date.fromisoformat(args.date) if args.date else date.today()

    # 1) Build & save universe
    universe = build_daily_universe(max_names=200)
    save_universe_for_date(universe, target_date)

    # 2) Recompute strategy metrics
    recompute_strategy_metrics()

    # 3) Build daily run plan
    build_daily_run_plan(for_date=target_date, mode=args.mode)


if __name__ == "__main__":  # pragma: no cover
    main()
