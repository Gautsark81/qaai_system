from .utils import run_cmd, log_markdown
import shutil


def git_summary():
    if not shutil.which("git"):
        log_markdown("🔁 Git Summary", "_git not available_")
        return {}
    branch = (
        run_cmd(["git", "rev-parse", "--abbrev-ref", "HEAD"]).get("stdout") or ""
    ).strip()
    last = (run_cmd(["git", "log", "-1", "--pretty=%h %s"]).get("stdout") or "").strip()
    dirty = bool(
        (run_cmd(["git", "status", "--porcelain"]).get("stdout") or "").strip()
    )
    md = f"- Branch: `{branch}`\n- Last commit: `{last}`\n- Uncommitted changes: `{dirty}`"
    log_markdown("🔁 Git Summary", md)
    return {"branch": branch, "last": last, "dirty": dirty}


def ci_mode_hint():
    log_markdown(
        "🔁 CI Mode", "Use `--ci` to produce status_summary.json for pipelines."
    )


def run_all():
    log_markdown("🔁 Automation & CI", "Git summary and CI hints below.")
    git_summary()
    ci_mode_hint()
