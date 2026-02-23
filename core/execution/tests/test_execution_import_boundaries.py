import ast
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[3]
CORE_EXECUTION_DIR = PROJECT_ROOT / "core" / "execution"

FORBIDDEN_IMPORT_PREFIXES = [
    "core.execution.engine",
    "core.execution.execute",
    "core.execution.broker",
]


def extract_imports(path: Path):
    with open(path, "rb") as f:
        raw = f.read()

    text = raw.decode("utf-8", errors="ignore")

    try:
        tree = ast.parse(text)
    except Exception:
        return []

    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

    return imports


def is_production_file(path: Path) -> bool:
    normalized = str(path).replace("\\", "/")

    # Skip tests
    if "/tests/" in normalized:
        return False

    # Skip scripts
    if "/scripts/" in normalized:
        return False

    # Skip examples
    if "/examples/" in normalized:
        return False

    # Skip virtual env
    if "/venv/" in normalized:
        return False

    return True


def test_execution_engine_imported_only_within_core():
    violations = []

    for py_file in PROJECT_ROOT.rglob("*.py"):

        if not is_production_file(py_file):
            continue

        # Skip core/execution itself
        if CORE_EXECUTION_DIR in py_file.parents:
            continue

        imports = extract_imports(py_file)

        for imp in imports:
            for forbidden in FORBIDDEN_IMPORT_PREFIXES:
                if imp.startswith(forbidden):
                    violations.append(str(py_file))

    assert not violations, (
        "Execution engine imported in production code outside core/execution:\n"
        + "\n".join(violations)
    )