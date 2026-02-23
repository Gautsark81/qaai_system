import json
import csv
from pathlib import Path
import matplotlib.pyplot as plt

OUTPUT_DIR = Path("outputs/screening/regime")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def emit_regime_artifacts(verdict):
    """
    Emit L3/L4 regime screening artifacts.
    """

    # ---------------------------
    # JSON snapshot (single verdict)
    # ---------------------------
    snapshot_path = OUTPUT_DIR / "verdicts.json"
    with snapshot_path.open("w") as f:
        json.dump(verdict.to_dict(), f, indent=2)

    # ---------------------------
    # CSV table (append)
    # ---------------------------
    table_path = OUTPUT_DIR / "regime_table.csv"
    write_header = not table_path.exists()

    evidence_map = {e.metric: e.value for e in verdict.evidence}

    with table_path.open("a", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "symbol",
                "eligible",
                "confidence",
                "failed_layer",
                "volatility_ratio",
                "trend_strength",
                "structural_break",
            ],
        )

        if write_header:
            writer.writeheader()

        writer.writerow({
            "symbol": verdict.symbol,
            "eligible": verdict.eligible,
            "confidence": verdict.confidence,
            "failed_layer": verdict.failed_layer.value if verdict.failed_layer else None,
            "volatility_ratio": evidence_map.get("volatility_ratio"),
            "trend_strength": evidence_map.get("trend_strength"),
            "structural_break": evidence_map.get("structural_break"),
        })


def emit_regime_distributions(rows):
    """
    Emit visual distributions (L4 proof).
    """

    vol_ratios = [r["volatility_ratio"] for r in rows]
    trend_strengths = [r["trend_strength"] for r in rows]

    # Volatility Ratio Distribution
    plt.figure()
    plt.hist(vol_ratios, bins=20)
    plt.title("Volatility Ratio Distribution")
    plt.xlabel("Realized / Long-run Volatility")
    plt.ylabel("Frequency")
    plt.savefig(OUTPUT_DIR / "volatility_ratio_distribution.png")
    plt.close()

    # Trend Strength Distribution
    plt.figure()
    plt.hist(trend_strengths, bins=20)
    plt.title("Trend Strength Distribution")
    plt.xlabel("Trend Strength")
    plt.ylabel("Frequency")
    plt.savefig(OUTPUT_DIR / "trend_strength_distribution.png")
    plt.close()
