import json
from pathlib import Path
import csv

import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs/screening/liquidity")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def emit_liquidity_artifacts(verdict):
    """
    Emit L3/L4 proof artifacts.
    """
    # ---------------------------
    # JSON snapshot (already used)
    # ---------------------------
    snapshot_path = OUTPUT_DIR / "verdicts.json"
    with snapshot_path.open("w") as f:
        json.dump(verdict.to_dict(), f, indent=2)

    # ---------------------------
    # CSV table (append mode)
    # ---------------------------
    table_path = OUTPUT_DIR / "liquidity_table.csv"
    write_header = not table_path.exists()

    with table_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "eligible",
                "confidence",
                "failed_layer",
                "order_pct_adv",
                "exit_days",
            ],
        )

        if write_header:
            writer.writeheader()

        evidence_map = {e.metric: e.value for e in verdict.evidence}

        writer.writerow({
            "symbol": verdict.symbol,
            "eligible": verdict.eligible,
            "confidence": verdict.confidence,
            "failed_layer": verdict.failed_layer.value if verdict.failed_layer else None,
            "order_pct_adv": evidence_map.get("order_pct_adv"),
            "exit_days": evidence_map.get("exit_days"),
        })


def emit_distributions(rows):
    """
    Emit visual distributions (L4 proof).
    """
    order_pct_adv = [r["order_pct_adv"] for r in rows]
    exit_days = [r["exit_days"] for r in rows]

    # Order % ADV
    plt.figure()
    plt.hist(order_pct_adv, bins=20)
    plt.title("Order Size as % of ADV")
    plt.xlabel("Order % ADV")
    plt.ylabel("Frequency")
    plt.savefig(OUTPUT_DIR / "order_pct_adv_distribution.png")
    plt.close()

    # Exit Days
    plt.figure()
    plt.hist(exit_days, bins=20)
    plt.title("Estimated Exit Days")
    plt.xlabel("Days")
    plt.ylabel("Frequency")
    plt.savefig(OUTPUT_DIR / "exit_days_distribution.png")
    plt.close()
