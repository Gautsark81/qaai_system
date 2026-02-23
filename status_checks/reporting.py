from .utils import log_markdown, write_markdown, report_assets_dir, run_cmd
import os
import glob

_last_coverage = 0.0


def generate_report(ci_mode=False):
    global _last_coverage
    res = run_cmd(["coverage", "report", "-m"])
    cov_txt = res.get("stdout") or res.get("stderr") or ""
    if cov_txt:
        lines = cov_txt.splitlines()
        total = None
        for L in lines:
            if L.strip().upper().startswith("TOTAL"):
                parts = L.split()
                if parts:
                    last = parts[-1]
                    if last.endswith("%"):
                        try:
                            total = float(last.rstrip("%"))
                        except Exception:
                            pass
        if total is not None:
            _last_coverage = total
        log_markdown("📈 Coverage Report", f"```\n{cov_txt[:4000]}\n```")

    # Embed assets
    assets = glob.glob(os.path.join(report_assets_dir, "*"))
    for a in assets:
        if a.lower().endswith((".png", ".jpg", ".jpeg")):
            log_markdown("🖼️ Asset", f"![]({a})")

    write_markdown("status_report.md")


def get_last_coverage():
    return _last_coverage
