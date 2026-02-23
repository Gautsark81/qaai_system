from .utils import run_cmd, log_markdown
import shutil


def run_ruff():
    if not shutil.which("ruff"):
        log_markdown("🔧 Ruff Linting", "_ruff not installed_")
        return {}
    res = run_cmd(["ruff", "check", ".", "--exit-zero", "--format", "json"])
    out = res.get("stdout") or res.get("stderr") or ""
    log_markdown("🔧 Ruff Linting", f"```\n{out[:4000]}\n```")
    return res


def run_mypy(target: str = "qaai_system"):
    if not shutil.which("mypy"):
        log_markdown("📐 Mypy Type Checking", "_mypy not installed_")
        return {}
    res = run_cmd(["mypy", target, "--ignore-missing-imports"])
    log_markdown(
        "📐 Mypy Type Checking", f"```\n{res.get('stdout') or res.get('stderr')}\n```"
    )
    return res


def run_radon(target: str = "qaai_system"):
    if not shutil.which("radon"):
        log_markdown("📊 Cyclomatic Complexity (radon)", "_radon not installed_")
        return {}
    res = run_cmd(["radon", "cc", target, "-s", "-a"])
    log_markdown(
        "📊 Cyclomatic Complexity (radon)",
        f"```\n{res.get('stdout') or res.get('stderr')}\n```",
    )
    return res


def run_all():
    log_markdown("🔧 Code Quality & Standards", "Ruff / Mypy / Radon results below.")
    run_ruff()
    run_mypy()
    run_radon()
