import ast
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[3]
LEGACY_EXECUTION_DIR = PROJECT_ROOT / "execution"


def safe_parse(path: Path):
    """
    Safely parse Python file, stripping BOM and ignoring encoding issues.
    """
    with open(path, "rb") as f:
        raw = f.read()

    text = raw.decode("utf-8", errors="ignore").lstrip("\ufeff")

    return ast.parse(text)


def extract_imports(path: Path):
    tree = safe_parse(path)
    imports = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            if node.module:
                imports.append(node.module)
        elif isinstance(node, ast.Import):
            for alias in node.names:
                imports.append(alias.name)

    return imports


def test_legacy_execution_does_not_import_core_execution():
    """
    Enforce single execution authority.

    The legacy /execution directory must not import from core.execution.
    """

    assert LEGACY_EXECUTION_DIR.exists(), "Legacy execution directory missing."

    violations = []

    for py_file in LEGACY_EXECUTION_DIR.rglob("*.py"):
        imports = extract_imports(py_file)

        for imp in imports:
            if imp.startswith("core.execution"):
                violations.append(str(py_file))

    assert not violations, (
        "Legacy execution imports core.execution (forbidden):\n"
        + "\n".join(violations)
    )