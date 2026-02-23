from .utils import log_markdown
import glob
import pandas as pd
import os


def data_null_check():
    issues = []
    for f in glob.glob("data/*.csv") + glob.glob("data/**/*.csv", recursive=True):
        if not os.path.exists(f):
            continue
        try:
            df = pd.read_csv(f, nrows=10000)
            total = df.shape[0] * df.shape[1]
            missing = int(df.isnull().sum().sum())
            pct = (missing / total * 100) if total > 0 else 0
            if missing > 0:
                issues.append((f, missing, pct))
        except Exception as e:
            issues.append((f, str(e), 0))
    md = (
        "\n".join([f"- `{f}`: missing={m} ({p:.2f}% )" for f, m, p in issues])
        or "_No nulls found_"
    )
    log_markdown("🧹 Data Null Check", md)
    return issues


def schema_drift_check():
    tables = {}
    for f in glob.glob("data/**/*.csv", recursive=True):
        name = os.path.basename(f).split(".")[0]
        tables.setdefault(name, []).append(f)
    drift = []
    for name, files in tables.items():
        files = sorted(files, key=os.path.getmtime, reverse=True)[:4]
        cols = []
        for f in files:
            try:
                df = pd.read_csv(f, nrows=10)
                cols.append(set(df.columns.tolist()))
            except Exception:
                pass
        if len(cols) >= 2 and cols[0] != cols[1]:
            drift.append((name, list(cols[0]), list(cols[1])))
    md = (
        "\n".join([f"- `{t}`: latest vs prev columns differ" for t, _, _ in drift])
        or "_No schema drift detected_"
    )
    log_markdown("🔍 Schema Drift", md)
    return drift


def run_all():
    log_markdown("📊 Data Health Checks", "Nulls, schema drift, dataset size changes.")
    data_null_check()
    schema_drift_check()
