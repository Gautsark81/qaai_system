"""
QAAI SYSTEM — PRODUCTION BOOTSTRAP (FINAL)

GUARANTEES:
- Zero-arg entrypoint
- Cold-start validation ALWAYS runs first
- Execution NEVER starts unless validation passes
- Deterministic bootstrap trade (paper only, optional)
"""

from __future__ import annotations

import os
import sys
import subprocess
import hashlib
import time
import traceback

from core.config.runtime_loader import load_runtime_config
from core.logging import get_logger


logger = get_logger("BOOT")


def _get_git_commit() -> str:
    try:
        return (
            subprocess.check_output(
                ["git", "rev-parse", "HEAD"],
                stderr=subprocess.DEVNULL,
            )
            .decode()
            .strip()
        )
    except Exception:
        return "UNKNOWN"


def _fingerprint_config() -> str:
    path = os.getenv("QAAI_CONFIG", "config/runtime.yaml")
    if not os.path.exists(path):
        raise SystemExit(f"Config file not found: {path}")

    h = hashlib.sha256()
    with open(path, "rb") as f:
        h.update(f.read())
    return h.hexdigest()


def bootstrap() -> None:
    try:
        cfg = load_runtime_config()

        mode = os.getenv("QAAI_MODE", "paper").lower()
        run_id = os.getenv("QAAI_RUN_ID")

        if mode not in ("paper", "live"):
            raise SystemExit(f"Invalid QAAI_MODE={mode}")

        if not run_id:
            raise SystemExit("QAAI_RUN_ID is required")

        logger.info("bootstrap_start mode=%s run_id=%s", mode, run_id)

        from core.runtime.run_context import RunContext
        from modules.state.state_store import StateStore
        from modules.execution.recovery.cold_start_validator import ColdStartValidator
        from modules.execution.orchestrator import ExecutionOrchestrator
        from modules.execution.recovery.reconciler import BrokerReconciler
        from modules.brokers.factory import BrokerFactory
        from modules.strategy.factory import build_strategies

        run_ctx = RunContext(
            run_id,
            _get_git_commit(),
            "PHASE_B_PRODUCTION",
            _fingerprint_config(),
            time.time(),
        )

        logger.info("run_context_ready run_id=%s", run_ctx.run_id)

        state_store = StateStore(run_ctx)
        broker = BrokerFactory.create(run_ctx)
        reconciler = BrokerReconciler(broker)

        ColdStartValidator(reconciler, state_store).validate()
        logger.info("cold_start_validation_passed")

        strategies = build_strategies(
            run_ctx=run_ctx,
            state_store=state_store,
            enabled=cfg.strategy.get("enabled", []),
        )

        orchestrator = ExecutionOrchestrator(
            run_ctx,
            broker,
            state_store,
        )

        logger.info("execution_start")
        orchestrator.start()

        # 🔒 Deterministic bootstrap validation (paper only)
        if cfg.bootstrap.get("deterministic_test_trade", False):
            if mode != "paper":
                raise SystemExit("Deterministic bootstrap trade forbidden outside paper")

            logger.warning("BOOT: deterministic bootstrap evaluation")

            for strategy in strategies:
                signals = strategy.evaluate({})
                for signal in signals:
                    orchestrator.handle_signal(signal)

    except SystemExit:
        raise
    except Exception as e:
        logger.error("BOOT_FATAL", exc_info=True)
        traceback.print_exc()
        sys.exit(1)
