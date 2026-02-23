#!/usr/bin/env python3
"""
MAX repo_scan.py
- parallel scanning (threads)
- progress bar (tqdm)
- skip large/binary files (size + extensions)
- optional HTML dashboard (jinja2)
- outputs JSON (default repo_scan.json)

Usage examples:
  python tools/repo_scan.py . --exclude "venv,Lib,site-packages,htmlcov" --workers 8 --max-size-bytes 2000000
  python tools/repo_scan.py . --dashboard-out reports/scan_report.html --workers 6
"""
from __future__ import annotations
import argparse
import concurrent.futures
import json
import re
import sys
import time
from pathlib import Path
from typing import Optional, Dict, Any, List, Set
import os

# Optional imports
try:
    from tqdm import tqdm
except Exception:
    tqdm = None  # safe fallback (no progress bar)

try:
    from jinja2 import Environment, FileSystemLoader, select_autoescape
except Exception:
    Environment = None

# tokens to search
TODO_PATTERN = re.compile(r"\b(TODO|FIXME|XXX|STUB)\b", re.IGNORECASE)

DEFAULT_MAX_BYTES = 1_000_000  # 1 MB
DEFAULT_WORKERS = min(8, (os.cpu_count() or 2) * 2)

# Default skip extensions (can be extended via --skip-extensions)
DEFAULT_SKIP_EXT: Set[str] = {
    ".png", ".jpg", ".jpeg", ".gif", ".mp4", ".pdf", ".zip", ".tar", ".gz", ".whl", ".egg", ".pyc", ".html"
}


def is_text_file(path: Path, skip_exts: Set[str]) -> bool:
    """Heuristic: skip binary-like files by extension or by reading first chunk."""
    if path.suffix.lower() in skip_exts:
        return False
    try:
        with path.open("rb") as fh:
            chunk = fh.read(1024)
            if b"\x00" in chunk:
                return False
    except Exception:
        return False
    return True


def scan_file(path: Path, max_bytes: int, skip_exts: Set[str]) -> Optional[Dict[str, Any]]:
    """Scan a single file for TODO-like tokens. Skip large or binary files."""
    try:
        if not path.is_file():
            return None
        try:
            size = path.stat().st_size
        except Exception:
            return None
        if size > max_bytes:
            return {"path": str(path), "skipped_large": True, "size": size}
        if not is_text_file(path, skip_exts):
            return {"path": str(path), "skipped_binary_ext": True, "size": size}
        todos = []
        with path.open("r", encoding="utf8", errors="ignore") as fh:
            for ln_no, line in enumerate(fh, start=1):
                m = TODO_PATTERN.search(line)
                if m:
                    todos.append({"line": ln_no, "token": m.group(0), "line_text": line.strip()})
        if todos:
            return {"path": str(path), "todos": todos, "size": size}
        return None
    except KeyboardInterrupt:
        raise
    except Exception as e:
        return {"path": str(path), "error": f"scan_failed: {e}"}


def collect_paths(root: Path, excludes: Set[str]) -> List[Path]:
    """Collect file paths under root while honoring excludes and ignoring VCS, node_modules."""
    paths = []
    for p in root.rglob("*"):
        try:
            rel = p.relative_to(root)
        except Exception:
            continue
        if any(part in excludes for part in rel.parts):
            continue
        if ".git" in rel.parts or ".svn" in rel.parts or "node_modules" in rel.parts:
            continue
        paths.append(p)
    return paths


def render_dashboard(out_html: Path, results: List[Dict[str, Any]], scanned_count: int, duration: float):
    """Render a simple HTML dashboard using jinja2 template located in tools/templates/"""
    if Environment is None:
        print("jinja2 not installed; cannot write HTML dashboard. Install jinja2 to enable this.")
        return
    # template folder is tools/templates beside this file
    tpl_dir = Path(__file__).resolve().parent / "templates"
    env = Environment(loader=FileSystemLoader(str(tpl_dir)), autoescape=select_autoescape(["html", "xml"]))
    tpl = env.get_template("repo_scan_report.html.j2")
    summary = {
        "scanned": scanned_count,
        "results_count": len(results),
        "duration_sec": round(duration, 2),
        "todos_count": sum(len(r.get("todos", [])) for r in results if "todos" in r),
        "skipped_large": sum(1 for r in results if r.get("skipped_large")),
        "skipped_binary": sum(1 for r in results if r.get("skipped_binary_ext")),
        "errors": sum(1 for r in results if r.get("error")),
    }
    html = tpl.render(summary=summary, results=results, generated_at=time.ctime())
    out_html.parent.mkdir(parents=True, exist_ok=True)
    out_html.write_text(html, encoding="utf8")
    print(f"Wrote HTML dashboard: {out_html}")


def main():
    parser = argparse.ArgumentParser(description="MAX repo_scan (parallel + dashboard + precommit helper)")
    parser.add_argument("root", nargs="?", default=".", help="root folder to scan")
    parser.add_argument("--exclude", default="", help="comma-separated excludes (folder / file names)")
    parser.add_argument("--out", default="repo_scan", help="output prefix (.json will be written)")
    parser.add_argument("--max-size-bytes", type=int, default=DEFAULT_MAX_BYTES)
    parser.add_argument("--workers", type=int, default=DEFAULT_WORKERS, help="number of parallel workers")
    parser.add_argument("--skip-extensions", default=",".join(sorted(DEFAULT_SKIP_EXT)), help="comma-separated suffixes to skip (e.g. .png,.zip)")
    parser.add_argument("--dashboard-out", default="", help="write HTML dashboard here (path). Requires jinja2.")
    parser.add_argument("--fail-on-todo", action="store_true", help="exit non-zero if any TODO/FIXME found (useful for CI)")
    args = parser.parse_args()

    root = Path(args.root).resolve()
    excludes = {s.strip() for s in args.exclude.split(",") if s.strip()}
    out_prefix = args.out
    max_bytes = int(args.max_size_bytes)
    workers = int(args.workers)
    skip_exts = {s.strip().lower() for s in args.skip_extensions.split(",") if s.strip()}

    all_paths = collect_paths(root, excludes)
    total_paths = len(all_paths)
    results: List[Dict[str, Any]] = []
    start = time.time()

    use_tqdm = tqdm is not None
    iterator = all_paths
    if use_tqdm:
        pbar = tqdm(total=total_paths, desc="Scanning files", unit="files")
    else:
        pbar = None

    # ThreadPool for IO bound scanning
    with concurrent.futures.ThreadPoolExecutor(max_workers=workers) as ex:
        future_to_path = {ex.submit(scan_file, p, max_bytes, skip_exts): p for p in iterator}
        for fut in concurrent.futures.as_completed(future_to_path):
            path = future_to_path[fut]
            try:
                entry = fut.result()
            except KeyboardInterrupt:
                raise
            except Exception as e:
                entry = {"path": str(path), "error": f"exception:{e}"}
            if entry:
                results.append(entry)
            if pbar:
                pbar.update(1)
    if pbar:
        pbar.close()

    duration = time.time() - start
    out_json = root / f"{out_prefix}.json"
    try:
        out_data = {"scanned": total_paths, "results": results, "duration_sec": duration}
        out_json.write_text(json.dumps(out_data, indent=2), encoding="utf8")
        print(f"Wrote: {out_json} (scanned={total_paths}, results={len(results)}, duration={duration:.2f}s)")
    except Exception as e:
        print("Failed to write results:", e, file=sys.stderr)

    if args.dashboard_out:
        try:
            render_dashboard(Path(args.dashboard_out), results, total_paths, duration)
        except Exception as e:
            print("Dashboard generation failed:", e, file=sys.stderr)

    if args.fail_on_todo:
        # Exit non-zero if any TODO-like token found
        todos_found = any("todos" in r for r in results)
        if todos_found:
            print("ERROR: TODO/FIXME tokens found; failing as requested (--fail-on-todo).")
            sys.exit(2)

    # Normal exit
    sys.exit(0)


if __name__ == "__main__":
    main()
