# tools/check_phase_dependencies.py

import ast
import sys
from phase_map import PHASE_MAP
from phase_rules import is_allowed

violations = []

def scan_file(path):
    tree = ast.parse(open(path).read())
    for node in ast.walk(tree):
        if isinstance(node, ast.ImportFrom):
            src_phase = resolve_phase(path)
            dst_phase = resolve_phase(node.module)
            if not is_allowed(src_phase, dst_phase):
                violations.append((path, src_phase, node.module, dst_phase))

if violations:
    for v in violations:
        print(f"❌ Phase violation: {v}")
    sys.exit(1)
