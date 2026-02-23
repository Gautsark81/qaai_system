import os
import subprocess
from datetime import datetime

# Colors for console output
RESET = "\033[0m"
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
CYAN = "\033[96m"
BOLD = "\033[1m"

# Shared markdown report buffer
report_lines = []
report_assets_dir = "report_assets"
os.makedirs(report_assets_dir, exist_ok=True)


def color(text: str, c: str = "") -> str:
    return f"{c}{text}{RESET}" if c else text


def init_report():
    global report_lines
    report_lines = []
    report_lines.append(
        f"# 📊 Project Status Report — {datetime.utcnow().isoformat()} UTC\n"
    )


def log_markdown(title: str, body: str = ""):
    report_lines.append(f"## {title}\n\n{body}\n")


def write_markdown(path: str = "status_report.md"):
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(report_lines))
    print(color(f"\n✅ Saved report: {path}", GREEN))


def run_cmd(cmd, cwd=None, timeout=None):
    """Run a command (list or string). Returns dict with stdout/stderr/returncode."""
    try:
        if isinstance(cmd, (list, tuple)):
            proc = subprocess.run(
                cmd,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
        else:
            proc = subprocess.run(
                cmd,
                shell=True,
                cwd=cwd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=timeout,
            )
        return {
            "stdout": proc.stdout,
            "stderr": proc.stderr,
            "returncode": proc.returncode,
        }
    except Exception as e:
        return {"stdout": "", "stderr": str(e), "returncode": 1}


def safe_read(path: str) -> str:
    try:
        with open(path, "r", encoding="utf-8") as f:
            return f.read()
    except Exception:
        return ""


def get_report_lines():
    return report_lines
