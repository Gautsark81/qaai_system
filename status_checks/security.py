from .utils import run_cmd, log_markdown
import shutil
import json


def run_bandit():
    if not shutil.which("bandit"):
        log_markdown("🔐 Bandit Security Scan", "_bandit not installed_")
        return {}
    res = run_cmd(["bandit", "-r", "qaai_system", "-f", "json"])
    log_markdown(
        "🔐 Bandit Security Scan", f"```\n{res.get('stdout') or res.get('stderr')}\n```"
    )
    return res


def run_license_audit():
    if not shutil.which("pip-licenses"):
        log_markdown("📜 License Audit", "_pip-licenses not installed_")
        return {}
    res = run_cmd(["pip-licenses", "--format=json"])
    out = res.get("stdout") or res.get("stderr") or ""
    try:
        parsed = json.loads(out)
        md = "\n".join(
            [
                f"- `{p.get('Name')}`: {p.get('License')}, version {p.get('Version')}"
                for p in parsed[:200]
            ]
        )
    except Exception:
        md = out[:4000]
    log_markdown("📜 License Audit", md)
    return res


def run_all():
    log_markdown("🔐 Security & Compliance", "Bandit / License audit below.")
    run_bandit()
    run_license_audit()
