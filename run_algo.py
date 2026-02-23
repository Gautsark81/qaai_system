from __future__ import annotations
import os
import sys
import time
import logging
import importlib
from pathlib import Path
from typing import Any, Dict

import yaml

# Prefer user's modules; fallback safely if unavailable
try:
    from qaai_system.execution.risk_manager import RiskManager  # type: ignore
    from qaai_system.execution.position_manager import PositionManager  # type: ignore
    from qaai_system.execution.orchestrator import ExecutionOrchestrator  # type: ignore
    from qaai_system.execution.portfolio_manager import PortfolioManager  # type: ignore
except Exception as e:
    print("ERROR: Required modules not found in qaai_system package:", e)
    sys.exit(1)

logging.basicConfig(
    level=os.getenv("LOG_LEVEL", "INFO"),
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler("runtime.log", mode="a", encoding="utf-8"),
    ],
)
log = logging.getLogger("run_algo")


def load_config(path: str) -> Dict[str, Any]:
    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_strategy(entry: Dict[str, str]):
    module = entry["module"]
    clsname = entry["class"]
    allocation = entry.get("allocation", 1.0)
    per_cap = entry.get("per_symbol_cap")
    m = importlib.import_module(module)
    cls = getattr(m, clsname)
    return cls(entry["id"], allocation=allocation, per_symbol_cap=per_cap)


def make_market_snapshot(symbols):
    # Replace with real feed; this mock keeps system running
    prices = {s: 100.0 for s in symbols}
    atr = {s: 1.0 for s in symbols}
    return {"symbols": symbols, "prices": prices, "atr": atr}


def main(cfg_path: str = "config.yaml"):
    cfg = load_config(cfg_path)

    risk = RiskManager(config=cfg.get("risk", {}))
    pm = PositionManager(method=(cfg.get("positions", {}) or {}).get("method", "fifo"))

    orch = ExecutionOrchestrator(
        provider=None,  # paper provider auto-injected by orchestrator
        router=None,
        feedback_target=None,
        risk=risk,
        positions=pm,
        config=cfg,
    )

    # Ensure PortfolioManager exists
    portfolio = getattr(orch, "portfolio_manager", None)
    if portfolio is None:
        portfolio = PortfolioManager(
            orchestrator=orch,
            risk_manager=risk,
            global_exposure_cap=(cfg.get("portfolio", {}) or {}).get(
                "global_exposure_cap"
            ),
        )

    # Register strategies
    for entry in cfg.get("strategies", []):
        strat = load_strategy(entry)
        portfolio.register_strategy(entry["id"], strat)

    symbols = cfg.get("symbols", ["RELIANCE"])
    log.info(
        "Starting Next-Gen Algo | mode=%s symbols=%s", cfg.get("mode", "paper"), symbols
    )

    # Main loop
    beat_ts = time.time()
    while True:
        try:
            # Heartbeat + risk breaker update
            equity = orch._get_equity_safe()
            risk.heartbeat(account_equity=equity)

            # Build market snapshot & generate portfolio plan
            md = make_market_snapshot(symbols)
            orders = portfolio.generate_portfolio_plan(md, account_equity=equity)

            # Submit orders
            for o in orders:
                try:
                    resp = orch.submit_order(o)
                    log.info("submit | %s", resp)
                except Exception as e:
                    log.warning("order rejected | %s | %s", o.get("symbol"), e)

            # Poll provider/orchestrator if available
            try:
                if hasattr(orch, "poll"):
                    orch.poll()
            except Exception:
                log.exception("poll failed")

            # Throttle
            time.sleep(3)

            # Periodic log
            if time.time() - beat_ts > 15:
                pos = pm.get_all_positions()
                log.info("heartbeat | equity=%.2f positions=%s", equity, pos)
                beat_ts = time.time()

        except KeyboardInterrupt:
            log.info("Stopping...")
            break
        except Exception:
            log.exception("main loop error; continuing")
            time.sleep(5)


if __name__ == "__main__":
    cfg_path = sys.argv[1] if len(sys.argv) > 1 else "config.yaml"
    if not Path(cfg_path).exists():
        # fall back to example
        Path("config.yaml").write_text(
            Path("config.example.yaml").read_text(encoding="utf-8"), encoding="utf-8"
        )
    main(cfg_path)
