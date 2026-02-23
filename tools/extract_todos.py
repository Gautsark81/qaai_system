#!/usr/bin/env python3
"""
extract_todos.py
Usage: python extract_todos.py project_audit.json repo_scan.json
Produces todo_backlog.csv with columns:
file, token, line, line_text, phase, severity
"""
import sys, json, csv, re, os

CRITICAL_PATHS = ["execution", "router", "risk", "infra", "db", "dhan", "position", "order", "trade", "providers"]

def classify_severity(path, token, line_text):
    p = path.replace("\\","/").lower()
    if any(cp in p for cp in CRITICAL_PATHS):
        return "blocking"
    # TODOs that mention 'security', 'kill', 'safety', 'token', 'credentials' are high
    if re.search(r"\b(kill|kill-switch|safet|security|credential|token|auth|unwind|reconcili)", (line_text or ""), re.I):
        return "high"
    # otherwise medium for TODO, low for comments like docs
    if token.upper() in ("FIXME","BUG"):
        return "high"
    if token.lower() in ("stub", "stubs"):
        return "medium"
    return "medium" if token.upper()=="TODO" else "low"

def extract_from_repo_scan(repo_scan):
    # repo_scan expected to contain "results": [{ "path": ..., "todos": [{ "line":..., "token":..., "line_text":...}, ...] }, ...]
    rows=[]
    for r in repo_scan.get("results", []):
        path = r.get("path") or r.get("File") or r.get("file") or ""
        todos = r.get("todos") or []
        for t in todos:
            token = t.get("token","TODO")
            line = t.get("line","")
            line_text = t.get("line_text","")
            severity = classify_severity(path, token, line_text)
            rows.append([path, token, line, line_text.replace("\n"," "), r.get("Phase",""), severity])
    return rows

def extract_from_project_audit(pa):
    # project_audit.json has "files":[{"File": "...", ...}] but likely not todos.
    # fallback: scan source files listed in project_audit.json if available on disk
    rows=[]
    for f in pa.get("files", []):
        path = f.get("File")
        if not path: continue
        if os.path.exists(path):
            try:
                with open(path, "r", encoding="utf8", errors="ignore") as fh:
                    for i, line in enumerate(fh, 1):
                        if "TODO" in line or "FIXME" in line or "Stub" in line or "stub" in line:
                            token = "TODO" if "TODO" in line else ("FIXME" if "FIXME" in line else "Stub")
                            severity = classify_severity(path, token, line)
                            rows.append([path, token, i, line.strip(), f.get("Phase",""), severity])
            except Exception:
                pass
    return rows

def main():
    args = sys.argv[1:]
    if not args:
        print("Usage: python extract_todos.py project_audit.json [repo_scan.json]")
        sys.exit(1)
    pa = {}
    repo = {}
    if os.path.exists(args[0]):
        try:
            pa = json.load(open(args[0], "r", encoding="utf8"))
        except Exception as e:
            pa = {}
    if len(args)>1 and os.path.exists(args[1]):
        try:
            repo = json.load(open(args[1], "r", encoding="utf8"))
        except Exception:
            repo = {}
    rows = []
    if repo:
        rows += extract_from_repo_scan(repo)
    if pa:
        rows += extract_from_project_audit(pa)
    # dedupe by file+token+line
    seen=set()
    out=[]
    for r in rows:
        key=(r[0], str(r[1]), str(r[2]))
        if key in seen: continue
        seen.add(key)
        out.append(r)
    out.sort(key=lambda x: (x[5], x[0]))  # sort by severity then file
    with open("todo_backlog.csv","w",newline="",encoding="utf8") as f:
        w=csv.writer(f)
        w.writerow(["file","token","line","line_text","phase","severity"])
        w.writerows(out)
    print(f"Wrote todo_backlog.csv ({len(out)} rows)")

if __name__=="__main__":
    main()
