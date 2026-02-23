# tools/apply_patch_orchestrator_fix_fixed.py
import io
import os
import sys
import re

PATCH_MARKER = "# ---- PATCH-START: EARLY-SAFETY-CHECKS ----"
PATCH_END_MARKER = "# ---- PATCH-END: EARLY-SAFETY-CHECKS ----"

patch_block = r"""
    # ---- PATCH-START: EARLY-SAFETY-CHECKS ----
    # Defensive initialization to avoid UnboundLocalError and perform early checks.
    rm = getattr(self, "risk", None)
    provider = getattr(self, "provider", None)
    cfg = getattr(self, "_cfg", {}) or {}

    nav = None
    pos = {}
    max_sym_early = None

    try:
        if provider is not None:
            nav_raw = getattr(provider, "_account_nav", None)
            try:
                nav = float(nav_raw) if nav_raw is not None else None
            except Exception:
                nav = None
            pos = dict(getattr(provider, "_positions", {}) or {})
    except Exception:
        nav = None
        pos = {}

    # CIRCUIT BREAKER EARLY CHECK
    try:
        if rm is not None and hasattr(rm, "is_trading_allowed"):
            acct_eq = nav if nav is not None else getattr(rm, "_current_equity", None)
            try:
                allowed = rm.is_trading_allowed(account_equity=acct_eq)
            except TypeError:
                allowed = rm.is_trading_allowed()
            if not allowed:
                raise ValueError("Trading not allowed by circuit breaker")
    except ValueError:
        raise
    except Exception:
        logger = getattr(self, "_logger", None)
        if logger:
            logger.debug("Circuit-breaker quick check failed (non-fatal)")

    # EARLY SYMBOL-CAP CHECK
    try:
        max_sym_w = None
        if rm is not None and getattr(rm, "config", None):
            try:
                max_sym_w = rm.config.get("max_symbol_weight", None)
            except Exception:
                max_sym_w = None
        if max_sym_w is None:
            max_sym_w = cfg.get("risk", {}).get("max_symbol_weight", None)

        if max_sym_w:
            symbol = None
            if isinstance(order, dict):
                symbol = order.get("symbol") or order.get("symbol_name") or order.get("s")
            if symbol:
                curr_qty = float(pos.get(symbol, 0) or 0)
                last_price_key = f"__last_price__:{symbol}"
                last_price = float(pos.get(last_price_key, order.get("price") or 0) or 0)
                order_qty = float(order.get("quantity") or order.get("qty") or 0)
                order_price = float(order.get("price") or last_price or 0)
                projected_value = (curr_qty + order_qty) * order_price
                if nav is not None and projected_value > float(max_sym_w) * float(nav):
                    raise ValueError(f"Symbol cap exceeded for {symbol}")
    except ValueError:
        raise
    except Exception:
        logger = getattr(self, "_logger", None)
        if logger:
            logger.debug("Early symbol-cap check failed (non-fatal)")
    # ---- PATCH-END: EARLY-SAFETY-CHECKS ----
"""


def find_and_insert_patch(file_path: str) -> bool:
    with io.open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    if PATCH_MARKER in text:
        print("[apply] Patch marker already present in", file_path)
        return False

    # Find def patched_submit_order signature
    m = re.search(
        r"(^\s*def\s+patched_submit_order\s*\([^)]*\)\s*:\s*\n)", text, flags=re.M
    )
    if not m:
        print("[apply] Could not find 'def patched_submit_order' in", file_path)
        return False

    insert_pos = m.end()
    new_text = text[:insert_pos] + patch_block + text[insert_pos:]

    bak_path = file_path + ".bak"
    with io.open(bak_path, "w", encoding="utf-8") as f:
        f.write(text)
    print("[apply] Backup written to", bak_path)

    with io.open(file_path, "w", encoding="utf-8") as f:
        f.write(new_text)

    print("[apply] Patched", file_path)
    return True


def main():
    repo_root = os.getcwd()
    candidate = os.path.join(repo_root, "patch_orchestrator.py")
    if not os.path.exists(candidate):
        print("[apply] Couldn't find patch_orchestrator.py in", repo_root)
        sys.exit(2)

    ok = find_and_insert_patch(candidate)
    if not ok:
        sys.exit(1)
    print("[apply] Done. Run the focused tests next.")


if __name__ == "__main__":
    main()
