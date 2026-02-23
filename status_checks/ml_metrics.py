from .utils import log_markdown, report_assets_dir
import os
import json
import glob


def backtest_summary():
    candidates = ["logs/backtest_results.json"] + glob.glob("results/backtest_*.json")
    for c in candidates:
        if os.path.exists(c):
            try:
                data = json.load(open(c, "r", encoding="utf-8"))
                sharpe = data.get("Sharpe") or data.get("sharpe")
                dd = data.get("Drawdown") or data.get("max_drawdown")
                md = f"- File: `{c}`\n- Sharpe: `{sharpe}`\n- Max Drawdown: `{dd}`\n"
                log_markdown("📈 Backtest Results", md)

                eq = data.get("equity_curve") or data.get("equity")
                if eq and isinstance(eq, list):
                    try:
                        import matplotlib.pyplot as plt

                        plt.figure()
                        plt.plot(eq)
                        pth = os.path.join(report_assets_dir, "equity_curve.png")
                        plt.title("Equity Curve")
                        plt.xlabel("Period")
                        plt.ylabel("Equity")
                        plt.savefig(pth)
                        plt.close()
                        log_markdown("📈 Equity Curve Image", f"![]({pth})")
                    except Exception:
                        pass
                return data
            except Exception:
                continue
    log_markdown("📈 Backtest Results", "_No backtest JSON found_")
    return {}


def signal_summary():
    files = glob.glob("data/signals/*.csv")
    summary_lines = []
    for f in files:
        try:
            import pandas as pd

            df = pd.read_csv(f)
            buys = (
                int((df["signal"] == "buy").sum()) if "signal" in df.columns else None
            )
            sells = (
                int((df["signal"] == "sell").sum()) if "signal" in df.columns else None
            )
            summary_lines.append(f"- `{f}`: rows={len(df)}, buys={buys}, sells={sells}")
        except Exception as e:
            summary_lines.append(f"- `{f}`: error reading ({e})")
    log_markdown("🔔 Signals Summary", "\n".join(summary_lines) or "_No signals found_")
    return files


def run_all():
    log_markdown("📈 ML / Trading Metrics", "Backtests, signals, portfolio snapshots")
    backtest_summary()
    signal_summary()
