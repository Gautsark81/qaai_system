import ast
import sys
from pathlib import Path

FORBIDDEN_IMPORTS = {
    "modules.portfolio",
    "modules.capital",
    "modules.regime",
}

PHASE_12_ROOTS = [
    "modules/execution",
    "modules/risk",
    "modules/strategies",
    "modules/core",
]


def scan_file(path: Path) -> list[str]:
    tree = ast.parse(path.read_text())
    violations = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for n in node.names:
                for forbidden in FORBIDDEN_IMPORTS:
                    if n.name.startswith(forbidden):
                        violations.append(f"{path}: imports {n.name}")
        elif isinstance(node, ast.ImportFrom):
            if node.module:
                for forbidden in FORBIDDEN_IMPORTS:
                    if node.module.startswith(forbidden):
                        violations.append(f"{path}: imports {node.module}")
    return violations


def main():
    errors = []

    for root in PHASE_12_ROOTS:
        for path in Path(root).rglob("*.py"):
            errors.extend(scan_file(path))

    if errors:
        print("❌ Phase boundary violations detected:\n")
        for e in errors:
            print(e)
        sys.exit(1)

    print("✅ Phase boundary check passed")


if __name__ == "__main__":
    main()
