"""
QAAI SYSTEM — INSTITUTIONAL BOOTSTRAP

INSTITUTIONAL GUARANTEES:
- CONFIG frozen before any broker import
- No os.getenv() allowed
- Mode strictly enforced
- Live requires explicit confirmation
- Capital envelope printed before execution
- Fail-closed architecture
"""

from __future__ import annotations

import sys
import time
import traceback
import hashlib
import subprocess

from env_validator import CONFIG  # 🔐 FROZEN CONFIG


# ─────────────────────────────────────────────
# Safe Logger
# ─────────────────────────────────────────────
def _get_logger():
    try:
        from core.logging import get_logger
        return get_logger("BOOT")
    except Exception:
        return None


_LOG = _get_logger()


def _log(level: str, msg: str):
    if _LOG:
        getattr(_LOG, level.lower(), _LOG.info)(msg)
    else:
        print(f"[{level.upper()}] {msg}", file=sys.stderr)


# ─────────────────────────────────────────────
# Deterministic Metadata
# ─────────────────────────────────────────────
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


def _config_hash() -> str:
    payload = repr(CONFIG).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


# ─────────────────────────────────────────────
# LIVE CONFIRMATION HANDSHAKE
# ─────────────────────────────────────────────
def _live_confirmation_gate():

    print("\n⚠️  LIVE MODE ACTIVATION ⚠️")
    print(f"Capital Envelope: {CONFIG.max_capital_pct}%")
    print(f"Max Daily Drawdown: {CONFIG.max_daily_drawdown_pct}%")
    print("Type EXACTLY: I_ACCEPT_LIVE_RISK")

    confirm = input("Confirmation: ").strip()

    if confirm != "I_ACCEPT_LIVE_RISK":
        raise SystemExit("Live confirmation failed.")


# ─────────────────────────────────────────────
# BOOTSTRAP ENTRYPOINT
# ─────────────────────────────────────────────
def bootstrap() -> None:

    try:

        _log("info", f"bootstrap_start mode={CONFIG.mode}")

        # ─────────────────────────────────────
        # HARD STOP — Global Kill Switch
        # ─────────────────────────────────────
        if CONFIG.global_kill_switch:
            raise SystemExit("GLOBAL_KILL_SWITCH enabled — aborting.")

        # ─────────────────────────────────────
        # LIVE GATE
        # ─────────────────────────────────────
        if CONFIG.mode == "live":
            _live_confirmation_gate()

        # ─────────────────────────────────────
        # Immutable Run Metadata
        # ─────────────────────────────────────
        git_commit = _get_git_commit()
        config_hash = _config_hash()
        start_time = time.time()

        _log("info", f"git_commit={git_commit}")
        _log("info", f"config_hash={config_hash}")

        # ─────────────────────────────────────
        # IMPORTS AFTER CONFIG FREEZE
        # ─────────────────────────────────────
        from core.runtime.run_context import RunContext
        from modules.state.state_store import StateStore
        from modules.execution.recovery.cold_start_validator import ColdStartValidator
        from modules.execution.recovery.reconciler import BrokerReconciler
        from modules.execution.orchestrator import ExecutionOrchestrator
        from modules.brokers.factory import BrokerFactory

        # ─────────────────────────────────────
        # RUN CONTEXT
        # ─────────────────────────────────────
        run_ctx = RunContext(
            run_id=str(int(start_time)),
            git_commit=git_commit,
            phase_version="INSTITUTIONAL_PHASE",
            config_fingerprint=config_hash,
            start_time=start_time,
        )

        state_store = StateStore(run_ctx)

        # ─────────────────────────────────────
        # MODE-SAFE BROKER INITIALIZATION
        # ─────────────────────────────────────
        if CONFIG.mode == "paper":
            broker = BrokerFactory.create_paper(run_ctx)

        elif CONFIG.mode == "shadow":
            broker = BrokerFactory.create_shadow(run_ctx)

        elif CONFIG.mode == "live":
            broker = BrokerFactory.create_live(run_ctx)

        else:
            raise SystemExit("Invalid mode detected.")

        reconciler = BrokerReconciler(broker)

        # ─────────────────────────────────────
        # COLD START VALIDATION
        # ─────────────────────────────────────
        ColdStartValidator(
            reconciler,
            state_store,
        ).validate()

        _log("info", "cold_start_validation_passed")

        # ─────────────────────────────────────
        # EXECUTION LAST
        # ─────────────────────────────────────
        if not CONFIG.execution_enabled:
            _log("info", "Execution disabled — exiting cleanly.")
            return

        orchestrator = ExecutionOrchestrator(
            run_ctx,
            broker,
            state_store,
        )

        _log("info", "execution_start")
        orchestrator.start()

        print("[EXECUTION STARTED]")

    except SystemExit as e:
        _log("error", f"BOOT_FATAL (SystemExit): {e}")
        raise

    except Exception as e:
        _log("error", f"BOOT_FATAL (Exception): {e}")
        traceback.print_exc()
        raise SystemExit(1)