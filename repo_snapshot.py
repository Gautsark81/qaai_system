# repo_snapshot.py
import os, json, hashlib, sys, pathlib, fnmatch, time

root = os.path.abspath(".")
out = {"root": root, "generated_at": time.time(), "files": [], "summary": {}}

# gather files (skip common big dirs)
skip_dirs = {".git", "venv", "__pycache__", ".pytest_cache", "node_modules", "data", "models"}
big_extensions = {".pt", ".pth", ".h5", ".zip", ".tar", ".gz", ".parquet", ".sqlite", ".db"}

total_size = 0
language_counts = {}
extensions = {}
largest = []

for dirpath, dirnames, filenames in os.walk(root):
    # prune skip dirs
    dirnames[:] = [d for d in dirnames if d not in skip_dirs]
    for f in filenames:
        p = os.path.join(dirpath, f)
        rel = os.path.relpath(p, root)
        try:
            st = os.stat(p)
            size = st.st_size
        except Exception:
            size = None
        total_size += size or 0
        ext = os.path.splitext(f)[1].lower()
        extensions.setdefault(ext, 0)
        extensions[ext] += 1
        # coarse language inference
        lang = "other"
        if ext in {".py"}:
            lang = "python"
        elif ext in {".md"}:
            lang = "markdown"
        elif ext in {".yml", ".yaml"}:
            lang = "yaml"
        elif ext in {".json"}:
            lang = "json"
        language_counts[lang] = language_counts.get(lang, 0) + 1

        largest.append((size or 0, rel))
        out["files"].append({"path": rel, "size": size, "ext": ext})
# sort largest
largest.sort(reverse=True)
out["summary"]["total_files"] = len(out["files"])
out["summary"]["total_size_bytes"] = total_size
out["summary"]["largest_files"] = [{"path": p, "size": s} for s, p in largest[:50]]
out["summary"]["extensions"] = dict(extensions)
out["summary"]["language_counts"] = language_counts

# check for key project files
keys = ["requirements.txt", "pyproject.toml", "setup.py", ".github/workflows", "tests", "todo_backlog.csv", "project_audit.json", "status_report.md"]
for k in keys:
    out["summary"]["has_"+k] = os.path.exists(os.path.join(root, k)) or os.path.exists(os.path.join(root, k.lstrip("./")))

# compute LOC for python files (fast)
py_loc = 0
py_files = 0
for f in out["files"]:
    if f["ext"] == ".py":
        p = os.path.join(root, f["path"])
        try:
            with open(p, "rb") as fh:
                lines = fh.read().count(b"\n")
            py_loc += lines
            py_files += 1
        except Exception:
            pass
out["summary"]["python_files"] = py_files
out["summary"]["python_loc"] = py_loc

# optionally compute top TODO counts across files
todo_hits = []
for f in out["files"]:
    if f["ext"] == ".py" or f["ext"] in {".md", ".txt", ".yml", ".yaml"}:
        p = os.path.join(root, f["path"])
        try:
            with open(p, "r", encoding="utf8", errors="ignore") as fh:
                txt = fh.read()
        except Exception:
            continue
        todos = txt.count("TODO") + txt.count("FIXME")
        if todos:
            todo_hits.append({"path": f["path"], "todos": todos})
out["summary"]["files_with_todos"] = sorted(todo_hits, key=lambda x: -x["todos"])[:200]

# dump to file
outp = "repo_snapshot.json"
with open(outp, "w", encoding="utf8") as fh:
    json.dump(out, fh, indent=2)
print(outp)
