"""
🚀 Supercharged QA-AI Project Audit Engine (Enhanced v2)
Includes safety fixes, dynamic paths, and improved logging.
"""

import os
import json
import subprocess
import pandas as pd
from datetime import datetime
from status_report import generate_status_report


# === Helper: Safe command runner ===
def run(cmd):
    try:
        proc = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return proc.stdout.strip()
    except Exception:
        return ""


# === Map file -> Phase ===
def map_phase(fname):
    mapping = {
        "env": "Phase 0 – Foundation",
        "db": "Phase 1 – Data Infrastructure",
        "data": "Phase 1 – Data Infrastructure",
        "feature": "Phase 2 – Feature Engineering",
        "ml": "Phase 3 – ML Brain",
        "risk": "Phase 4 – Risk Management",
        "trade": "Phase 5 – Execution Layer",
        "backtest": "Phase 6 – Backtest & Paper",
        "dashboard": "Phase 7 – Monitoring",
        "audit": "Phase 8 – Compliance",
        "rl": "Phase 9+ – Self-Learning",
    }
    for k, v in mapping.items():
        if k in fname.lower():
            return v
    return "Miscellaneous"


# === Detect recent changes ===
def detect_changes():
    diff = run("git diff --name-only HEAD~1 HEAD")
    return diff.splitlines() if diff else []


# === Core Analyzer ===
def super_audit(project_path=None):
    print("🚀 Running Super Audit...")
    project_path = project_path or os.getcwd()
    files = []
    changed = detect_changes()

    for root, _, fs in os.walk(project_path):
        for f in fs:
            if f.endswith((".py", ".md", ".yaml", ".json")):
                path = os.path.join(root, f)
                try:
                    size = os.path.getsize(path)
                    modified = datetime.fromtimestamp(os.path.getmtime(path)).strftime(
                        "%Y-%m-%d %H:%M"
                    )
                    with open(path, "r", encoding="utf-8", errors="ignore") as fp:
                        text = fp.read()
                    status = (
                        "Initial"
                        if not text.strip()
                        else (
                            "Partial"
                            if "TODO" in text or "pass" in text
                            else "Complete"
                        )
                    )
                    changed_flag = "🆕" if path in changed else ""
                    files.append(
                        {
                            "File": os.path.relpath(path, project_path),
                            "Phase": map_phase(f),
                            "Status": status,
                            "Changed": changed_flag,
                            "SizeKB": round(size / 1024, 2),
                            "LastModified": modified,
                        }
                    )
                except Exception as e:
                    print(f"⚠️ Skipped {path}: {e}")

    if not files:
        print("❌ No auditable files found. Check project path.")
        return

    df = pd.DataFrame(files)
    df.to_csv("phase_audit_report.csv", index=False)

    # ✅ FIX: Only group if 'Phase' exists
    if "Phase" in df.columns and not df.empty:
        summary = df.groupby("Phase")["Status"].value_counts().unstack(fill_value=0)
        summary["TotalFiles"] = summary.sum(axis=1)
        summary["Completion%"] = (
            summary.get("Complete", 0) / summary["TotalFiles"] * 100
        ).round(2)
    else:
        summary = pd.DataFrame(
            columns=[
                "Phase",
                "Complete",
                "Partial",
                "Initial",
                "TotalFiles",
                "Completion%",
            ]
        )

    summary.to_csv("phase_summary.csv")
    print("✅ Reports generated → phase_audit_report.csv, phase_summary.csv")

    try:
        generate_status_report(project_path)
    except Exception as e:
        print(f"⚠️ status_report.py skipped: {e}")

    json.dump(
        {
            "last_run": datetime.now().isoformat(),
            "summary": summary.to_dict(),
            "files": df.to_dict(orient="records"),
        },
        open("project_audit.json", "w"),
        indent=2,
    )

    print("📊 JSON export → project_audit.json")
    return df, summary


if __name__ == "__main__":
    super_audit()
