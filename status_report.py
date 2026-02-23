import os
import re
import subprocess
import json
from typing import List, Tuple, Dict, Any
import requests
import types
import ast


# -------------------------------------------------------------------------
# Logging helper
# -------------------------------------------------------------------------
def log_step(msg: str):
    """Print progress messages during status report generation."""
    print(f"👉 {msg}", flush=True)


# -------------------------------------------------------------------------
# Pytest parsing utilities
# -------------------------------------------------------------------------
def parse_pytest_counts(output: str) -> Tuple[int, int, int, int, int]:
    """Parse pytest output and return counts of passed, failed, xfailed, errors, collected."""
    collected = 0
    passed = failed = xfailed = errors = 0
    for line in output.splitlines():
        if line.startswith("collected"):
            m = re.search(r"collected\s+(\d+)", line)
            if m:
                collected = int(m.group(1))
        if "passed" in line or "failed" in line or "error" in line:
            parts = line.split(",")
            for part in parts:
                part = part.strip()
                if part.endswith("passed"):
                    passed = int(part.split()[0])
                elif part.endswith("failed"):
                    failed = int(part.split()[0])
                elif part.endswith("xfailed"):
                    xfailed = int(part.split()[0])
                elif part.endswith("error") or part.endswith("errors"):
                    errors = int(part.split()[0])
    return passed, failed, xfailed, errors, collected


# -------------------------------------------------------------------------
# Coverage parsing
# -------------------------------------------------------------------------
def parse_coverage_total_percent(report_text: str) -> float:
    """Extract the TOTAL coverage percentage from a coverage report."""
    m = re.search(r"TOTAL\s+\d+\s+\d+\s+(\d+)%", report_text)
    return float(m.group(1)) if m else 0.0


def parse_coverage_file_percentages(report_text: str) -> List[Tuple[str, float]]:
    """Parse per-file coverage percentages from a coverage report."""
    rows = []
    for line in report_text.splitlines():
        m = re.match(r"(\S+\.py).*?(\d+)%", line)
        if m:
            rows.append((m.group(1), float(m.group(2))))
    return rows


# -------------------------------------------------------------------------
# Progress scoring
# -------------------------------------------------------------------------
def compute_progress_score(
    test_summary: Dict[str, int],
    coverage_pct: float,
    stub_list: List[Tuple[str, List[Tuple[int, str]]]],
    dhan_present: bool,
    pm_present: bool,
) -> Dict[str, Any]:
    collected = test_summary.get("collected", 0)
    passed = test_summary.get("passed", 0)

    # Test points: up to 50
    test_points = (passed / collected) * 50.0 if collected > 0 else 0.0

    # Coverage points: up to 30, full credit if >=95%
    cov_points = 30.0 if coverage_pct >= 95.0 else (coverage_pct / 100.0) * 30.0

    # Stub points bucket
    stub_count = sum(len(items) for _, items in stub_list)
    stub_points = 10.0 if stub_count == 0 else min(20.0, stub_count * 5.0)

    # Bonuses for dhan/pm presence
    presence_bonus = (10.0 if dhan_present else 0.0) + (10.0 if pm_present else 0.0)

    # Core points = stub bucket
    core_points = stub_points

    # Total
    total = test_points + cov_points + presence_bonus + stub_points
    if total > 100.0:
        total = 100.0

    return {
        "test_points": round(test_points, 2),
        "cov_points": round(cov_points, 2),
        "stub_points": round(stub_points, 2),
        "presence_bonus": round(presence_bonus, 2),
        "core_points": round(core_points, 2),
        "percent": round(total, 2),
        # Metadata
        "collected": collected,
        "passed": passed,
        "coverage_pct": coverage_pct,
        "stub_count": stub_count,
    }


# -------------------------------------------------------------------------
# Progress bar rendering
# -------------------------------------------------------------------------
def render_progress_bar(percent: float, length: int = 30) -> str:
    """Render a simple text-based progress bar."""
    filled = int(length * percent // 100)
    bar = "█" * filled + "░" * (length - filled)
    return f"[{bar}] {percent:.0f}%"


# -------------------------------------------------------------------------
# Command runner
# -------------------------------------------------------------------------
def run_cmd(cmd: List[str]) -> types.SimpleNamespace:
    """Run a shell command and return a SimpleNamespace with stdout, stderr, returncode."""
    try:
        proc = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=False,
            shell=(os.name == "nt"),
        )
        return types.SimpleNamespace(
            stdout=proc.stdout.strip(),
            stderr=proc.stderr.strip(),
            returncode=proc.returncode,
        )
    except Exception as e:
        return types.SimpleNamespace(stdout="", stderr=str(e), returncode=1)


# -------------------------------------------------------------------------
# Smoke & full tests
# -------------------------------------------------------------------------
def run_smoke_tests() -> Tuple[bool, Dict[str, int]]:
    """Run quick pytest smoke tests and return success flag and summary dict."""
    res = run_cmd(["pytest", "-q", "--maxfail=1", "--disable-warnings"])
    passed, failed, xfailed, errors, collected = parse_pytest_counts(res.stdout)
    ok = res.returncode == 0 and failed == 0 and errors == 0
    summary = {
        "passed": passed,
        "failed": failed,
        "xfailed": xfailed,
        "errors": errors,
        "collected": collected,
    }
    return ok, summary


def run_full_tests_with_coverage() -> Dict[str, Any]:
    """Run full pytest with coverage reporting."""
    result: Dict[str, Any] = {}
    test_res = run_cmd(["pytest", "--maxfail=1", "--disable-warnings", "-q"])
    passed, failed, xfailed, errors, collected = parse_pytest_counts(test_res.stdout)
    result["test_summary"] = dict(
        passed=passed,
        failed=failed,
        xfailed=xfailed,
        errors=errors,
        collected=collected,
    )
    cov_res = run_cmd(["coverage", "report"])
    result["total_pct"] = parse_coverage_total_percent(cov_res.stdout)
    result["file_coverages"] = parse_coverage_file_percentages(cov_res.stdout)
    run_cmd(["coverage", "html"])
    return result


# -------------------------------------------------------------------------
# Code quality scans
# -------------------------------------------------------------------------
def count_todos_fixes(path: str):
    todos = fixmes = 0
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as fh:
                        text = fh.read()
                    todos += text.count("TODO")
                    fixmes += text.count("FIXME")
                except Exception:
                    continue
    return {"todos": todos, "fixmes": fixmes}


def detect_stubs(path: str):
    stubs = []
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as fh:
                        lines = fh.read().splitlines()

                    stub_lines = [
                        (i + 1, line.strip())
                        for i, line in enumerate(lines)
                        if line.strip() == "pass"
                    ]

                    if stub_lines:
                        stubs.append((file_path, stub_lines))

                except Exception:
                    continue
    return stubs

# -------------------------------------------------------------------------
# Function-level analysis
# -------------------------------------------------------------------------
def analyze_functions(path: str) -> Dict[str, Any]:
    """Analyze functions in each .py file and return project + per-file details."""
    details = {"files": {}, "totals": {"functions": 0, "stubs": 0, "lines": 0}}
    for root, _, files in os.walk(path):
        for f in files:
            if f.endswith(".py"):
                file_path = os.path.join(root, f)
                try:
                    with open(file_path, encoding="utf-8", errors="ignore") as fp:
                        source = fp.read()
                    tree = ast.parse(source, filename=file_path)
                    funcs = []
                    for node in ast.walk(tree):
                        if isinstance(node, ast.FunctionDef):
                            start = node.lineno
                            end = max(
                                [
                                    c.lineno
                                    for c in ast.walk(node)
                                    if hasattr(c, "lineno")
                                ],
                                default=start,
                            )
                            funcs.append(
                                {
                                    "name": node.name,
                                    "lines": end - start + 1,
                                    "stub": any(
                                        isinstance(c, ast.Pass) for c in ast.walk(node)
                                    ),
                                }
                            )
                    if funcs:
                        stub_count = sum(1 for fn in funcs if fn["stub"])
                        total_lines = sum(fn["lines"] for fn in funcs)
                        details["files"][file_path] = {
                            "summary": {
                                "functions": len(funcs),
                                "stubs": stub_count,
                                "lines": total_lines,
                            },
                            "functions": funcs,
                        }
                        details["totals"]["functions"] += len(funcs)
                        details["totals"]["stubs"] += stub_count
                        details["totals"]["lines"] += total_lines
                except Exception:
                    continue
    return details


# -------------------------------------------------------------------------
# Dependency audit
# -------------------------------------------------------------------------
def dependency_audit() -> List[Tuple[str, str, str]]:
    """Run pip-audit and return outdated dependencies as (name, current, latest)."""
    res = run_cmd(["pip-audit", "-f", "json"])
    try:
        data = json.loads(res.stdout)
        results = []
        for pkg in data:
            results.append((pkg["name"], pkg["version"], pkg.get("latest_version", "")))
        return results
    except Exception:
        results = []
        for line in res.stdout.splitlines():
            m = re.match(r"(\S+)\s+\(([\d\.]+)\)\s+->\s+([\d\.]+)", line)
            if m:
                results.append((m.group(1), m.group(2), m.group(3)))
        return results


# -------------------------------------------------------------------------
# Slack / Telegram notifications
# -------------------------------------------------------------------------
SLACK_WEBHOOK = os.getenv("SLACK_WEBHOOK", "")
TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN", "")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "")


def post_to_slack(title: str, msg: str) -> bool:
    """Post a message to Slack via webhook."""
    if not SLACK_WEBHOOK:
        return False
    payload = {"text": f"*{title}*\n{msg}"}
    try:
        res = requests.post(SLACK_WEBHOOK, json=payload)
        return res.status_code == 200
    except Exception:
        return False


def post_to_telegram(msg: str) -> bool:
    """Send a message to Telegram chat."""
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    try:
        res = requests.post(url, data={"chat_id": TELEGRAM_CHAT_ID, "text": msg})
        return res.status_code == 200
    except Exception:
        return False


# -------------------------------------------------------------------------
# Report generator
# -------------------------------------------------------------------------
def generate_status_report(
    project_path: str = ".", output_file: str = "status_report.md"
) -> str:
    """Generate a full status_report.md with tests, coverage, quality, and audit info."""
    report_sections = []

    log_step("Running smoke tests...")
    ok, summary = run_smoke_tests()

    log_step("Running full tests with coverage...")
    full = run_full_tests_with_coverage()

    log_step("Scanning code quality (TODOs, FIXMEs, stubs)...")
    todos = count_todos_fixes(project_path)
    stubs = detect_stubs(project_path)

    log_step("Analyzing functions per file...")
    func_details = analyze_functions(project_path)

    log_step("Checking dependencies...")
    outdated = dependency_audit()

    log_step("Computing progress score...")
    score = compute_progress_score(
        test_summary=full["test_summary"],
        coverage_pct=full["total_pct"],
        stub_list=stubs,
        dhan_present=True,
        pm_present=True,
    )

    # Build report
    report_sections.append("# 📋 Project Status Report\n")

    # Smoke tests
    report_sections.append("## ✅ Smoke Test Summary")
    report_sections.append(f"- Passed: {summary['passed']}")
    report_sections.append(f"- Failed: {summary['failed']}")
    report_sections.append(f"- Errors: {summary['errors']}")
    report_sections.append(f"- Collected: {summary['collected']}")
    report_sections.append(f"- Result: {'✔️ All good' if ok else '❌ Issues found'}\n")

    # Full tests & coverage
    report_sections.append("## 🧪 Full Test & Coverage")
    ts = full["test_summary"]
    report_sections.append(f"- Passed: {ts['passed']}")
    report_sections.append(f"- Failed: {ts['failed']}")
    report_sections.append(f"- Coverage: {full['total_pct']}%\n")

    report_sections.append("### Per-file Coverage")
    for f, pct in full["file_coverages"]:
        report_sections.append(f"- {f}: {pct}%")

    # Code quality
    report_sections.append("\n## 🔍 Code Quality")
    report_sections.append(f"- TODOs: {todos['todos']}")
    report_sections.append(f"- FIXMEs: {todos['fixmes']}")
    report_sections.append(f"- Stubs: {score['stub_count']}")

    # Dependencies
    report_sections.append("\n## 📦 Dependencies")
    if outdated:
        for pkg, cur, latest in outdated:
            report_sections.append(f"- {pkg}: {cur} → {latest}")
    else:
        report_sections.append("- All dependencies up-to-date.")

    # Progress score
    report_sections.append("\n## 📊 Progress Score")
    report_sections.append(f"- Test points: {score['test_points']}")
    report_sections.append(f"- Coverage points: {score['cov_points']}")
    report_sections.append(f"- Stub points: {score['stub_points']}")
    report_sections.append(f"- Core points: {score['core_points']}")
    report_sections.append(f"- Presence bonus: {score['presence_bonus']}")
    report_sections.append(f"- **Final Score: {score['percent']}%**")
    report_sections.append(render_progress_bar(score["percent"]))

    # Project-wide function summary
    totals = func_details["totals"]
    report_sections.append("\n## 📊 Project Function Summary")
    report_sections.append(
        f"- Total functions: {totals['functions']}\n"
        f"- Total stubs: {totals['stubs']}\n"
        f"- Total lines in functions: {totals['lines']}"
    )

    # Per-file function details
    report_sections.append("\n## 📂 Function-Level Details")
    for file, data in func_details["files"].items():
        summary = data["summary"]
        report_sections.append(
            f"\n### {file}\n"
            f"- Functions: {summary['functions']}\n"
            f"- Stubs: {summary['stubs']}\n"
            f"- Total lines in functions: {summary['lines']}"
        )
        for fn in data["functions"]:
            stub_flag = " (STUB)" if fn["stub"] else ""
            report_sections.append(
                f"  - `{fn['name']}`: {fn['lines']} lines{stub_flag}"
            )

    # Write to file
    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(report_sections))

    log_step(f"✅ Status report generated: {output_file}")
    return output_file


# -------------------------------------------------------------------------
# Script entrypoint
# -------------------------------------------------------------------------
if __name__ == "__main__":
    print("🔄 Generating project status report...")
    generate_status_report(".")
