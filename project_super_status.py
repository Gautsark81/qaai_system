#!/usr/bin/env python
"""
🚀 PROJECT SUPER STATUS — MASTER INTELLIGENCE SCANNER (v6)

FEATURES
--------
✔ Fast vs Full mode
✔ Parallel scanning
✔ venv / cache ignored (Windows-safe)
✔ BOM + syntax-error safe
✔ Phase completion + confidence
✔ Strategy coverage / heatmap
✔ Risk hotspot detection
✔ Exports: JSON, Markdown, CSV, Excel

SAFE BY DESIGN
--------------
• Static analysis only
• No runtime imports
• No async / scheduler execution
"""

from __future__ import annotations

import ast
import argparse
import csv
import json
import os
import time
from pathlib import Path
from typing import Dict, Any, List
from collections import Counter
from concurrent.futures import ThreadPoolExecutor, as_completed

# =============================================================================
# CONFIGURATION
# =============================================================================

EXCLUDE_DIRS = {
    ".git", ".venv", "venv", "__pycache__", ".pytest_cache",
    ".idea", ".vscode", "node_modules",
}

FAST_FILE_LIMIT = 500
FULL_FILE_LIMIT = 10_000
PROGRESS_EVERY = 50
MAX_WORKERS = min(32, os.cpu_count() or 4)

# =============================================================================
# PHASE DEFINITIONS
# =============================================================================

MASTER_PHASES = {
    "Phase 0": "Foundation",
    "Phase A": "Safety & Infra",
    "Phase B": "Execution Robustness",
    "Phase C": "Data Pipeline",
    "Phase D": "Strategy Factory",
    "Phase E": "Promotion & Meta-Model",
    "Phase F": "Autonomous Evolution",
}

PHASE_HINTS = {
    "config": "Phase 0",
    "infra": "Phase A",
    "risk": "Phase A",
    "execution": "Phase B",
    "order": "Phase B",
    "router": "Phase B",
    "data": "Phase C",
    "store": "Phase C",
    "feature": "Phase C",
    "strategy": "Phase D",
    "signal": "Phase D",
    "alpha": "Phase D",
    "optimizer": "Phase D",
    "lifecycle": "Phase E",
    "meta": "Phase E",
    "monitor": "Phase F",
    "health": "Phase F",
}

# Human-verified phase status (source of truth)
PHASE_STATUS = {
    "Phase 0": {"status": "complete", "confidence": 1.0},
    "Phase A": {"status": "complete", "confidence": 0.95},
    "Phase B": {"status": "in_progress", "confidence": 0.6},
    "Phase C": {"status": "partial", "confidence": 0.4},
    "Phase D": {"status": "not_started", "confidence": 0.0},
    "Phase E": {"status": "not_started", "confidence": 0.0},
    "Phase F": {"status": "not_started", "confidence": 0.0},
}

# =============================================================================
# STRATEGY COVERAGE (PHASE D READINESS)
# =============================================================================

STRATEGY_KEYS = ["strategy", "signal", "alpha", "optimizer", "meta"]

# =============================================================================
# STATIC RISK PATTERNS
# =============================================================================

RISK_PATTERNS = {
    "infinite_loop": "while True",
    "background_task": "asyncio.create_task",
    "scheduler": "schedule(",
    "reconnect_loop": "reconnect",
}

# =============================================================================
# HELPERS
# =============================================================================

def should_ignore(path: Path) -> bool:
    parts = {p.lower() for p in path.parts}
    return bool(parts & EXCLUDE_DIRS)


def detect_phase(path: str) -> str:
    lower = path.lower()
    for k, phase in PHASE_HINTS.items():
        if k in lower:
            return phase
    return "Unclassified"


def safe_read(path: Path) -> str:
    try:
        raw = path.read_bytes()
        if raw.startswith(b"\xef\xbb\xbf"):  # BOM
            raw = raw[3:]
        return raw.decode("utf-8", errors="ignore")
    except Exception:
        return ""


def analyze_file(path: Path, root: Path, mode: str) -> Dict[str, Any]:
    text = safe_read(path)
    rel = str(path.relative_to(root))

    info = {
        "path": rel,
        "lines": text.count("\n") + 1,
        "phase_hint": detect_phase(rel),
        "functions": [],
        "classes": [],
        "imports": [],
        "risks": [],
        "parse_ok": True,
        "is_test": rel.startswith("tests"),
    }

    for k, v in RISK_PATTERNS.items():
        if v in text:
            info["risks"].append(k)

    if mode == "fast" or not text.strip():
        return info

    try:
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.FunctionDef):
                info["functions"].append(node.name)
            elif isinstance(node, ast.ClassDef):
                info["classes"].append(node.name)
            elif isinstance(node, ast.Import):
                for n in node.names:
                    info["imports"].append(n.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                info["imports"].append(node.module)
    except SyntaxError:
        info["parse_ok"] = False

    return info

# =============================================================================
# PROJECT SCAN (PARALLEL)
# =============================================================================

def scan_project(root: Path, mode: str) -> Dict[str, Any]:
    limit = FAST_FILE_LIMIT if mode == "fast" else FULL_FILE_LIMIT

    files: Dict[str, Dict[str, Any]] = {}
    phase_counts = Counter()
    strategy_coverage = {k: 0 for k in STRATEGY_KEYS}

    candidates: List[Path] = []
    for p in root.rglob("*.py"):
        if should_ignore(p):
            continue
        candidates.append(p)
        if len(candidates) >= limit:
            break

    print(f"🔍 Scanning {len(candidates)} files ({mode} mode)")

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {
            pool.submit(analyze_file, p, root, mode): p
            for p in candidates
        }

        for i, fut in enumerate(as_completed(futures), 1):
            info = fut.result()
            files[info["path"]] = info
            phase_counts[info["phase_hint"]] += 1

            path_lower = info["path"].lower()
            for k in STRATEGY_KEYS:
                if k in path_lower:
                    strategy_coverage[k] += 1

            if i % PROGRESS_EVERY == 0 or i == len(candidates):
                print(f"[SCAN] {i}/{len(candidates)}")

    # Computed confidence blending (heuristic + human)
    total = sum(phase_counts.values()) or 1
    computed_conf = {}
    for phase in MASTER_PHASES:
        heuristic = phase_counts.get(phase, 0) / total
        human = PHASE_STATUS.get(phase, {}).get("confidence", 0)
        computed_conf[phase] = round((heuristic + human) / 2, 3)

    return {
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S"),
        "mode": mode,
        "file_count": len(files),
        "files": files,
        "phase_file_distribution": dict(phase_counts),
        "phase_status": PHASE_STATUS,
        "phase_confidence_computed": computed_conf,
        "strategy_coverage": strategy_coverage,
        "master_phases": MASTER_PHASES,
        "workflow_order": [
            "Add Phase Status to Tool",
            "Review Status JSON",
            "Start Phase A Fixes",
        ],
    }

# =============================================================================
# EXPORTS
# =============================================================================

def export_markdown(report: Dict[str, Any]) -> None:
    lines = ["# 🚀 Project Super Status\n"]
    lines.append(f"Generated: `{report['generated_at']}`")
    lines.append(f"Mode: `{report['mode']}`\n")

    lines.append("## 📊 Phase Status & Confidence")
    for p, meta in report["phase_status"].items():
        lines.append(
            f"- **{p} – {MASTER_PHASES[p]}** → "
            f"{meta['status']} "
            f"(confidence={report['phase_confidence_computed'][p]})"
        )

    lines.append("\n## 🧠 Strategy Coverage (Phase D Readiness)")
    for k, v in report["strategy_coverage"].items():
        lines.append(f"- `{k}`: {v} files")

    Path("project_super_status.md").write_text("\n".join(lines), encoding="utf-8")


def export_csv(report: Dict[str, Any]) -> None:
    with open("project_files.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "path", "phase_hint", "lines",
            "functions", "classes", "imports",
            "risks", "parse_ok",
        ])
        for file in report["files"].values():
            writer.writerow([
                file["path"],
                file["phase_hint"],
                file["lines"],
                len(file["functions"]),
                len(file["classes"]),
                ",".join(file["imports"]),
                ",".join(file["risks"]),
                file["parse_ok"],
            ])

    with open("strategy_coverage.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["key", "file_count"])
        for k, v in report["strategy_coverage"].items():
            writer.writerow([k, v])


def export_excel(report: Dict[str, Any]) -> None:
    try:
        import openpyxl
    except Exception:
        print("⚠️ openpyxl not installed — skipping Excel export")
        return

    wb = openpyxl.Workbook()

    ws = wb.active
    ws.title = "Files"
    ws.append([
        "Path", "Phase", "Lines",
        "Functions", "Classes", "Risks", "Parse OK"
    ])

    for f in report["files"].values():
        ws.append([
            f["path"],
            f["phase_hint"],
            f["lines"],
            len(f["functions"]),
            len(f["classes"]),
            ", ".join(f["risks"]),
            f["parse_ok"],
        ])

    ws2 = wb.create_sheet("Strategy Coverage")
    ws2.append(["Key", "File Count"])
    for k, v in report["strategy_coverage"].items():
        ws2.append([k, v])

    wb.save("project_files.xlsx")

# =============================================================================
# CLI
# =============================================================================

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=["fast", "full"],
        default="fast",
        help="Scan mode",
    )
    args = parser.parse_args()

    print("🚀 Project Super Status starting…")
    print(f"🚫 Ignoring directories: {sorted(EXCLUDE_DIRS)}")

    root = Path.cwd()
    report = scan_project(root, args.mode)

    Path("project_super_status.json").write_text(
        json.dumps(report, indent=2),
        encoding="utf-8",
    )

    export_markdown(report)
    export_csv(report)
    export_excel(report)

    print("✅ Generated outputs:")
    print(" - project_super_status.json")
    print(" - project_super_status.md")
    print(" - project_files.csv")
    print(" - strategy_coverage.csv")
    print(" - project_files.xlsx (if openpyxl installed)")


if __name__ == "__main__":
    main()
