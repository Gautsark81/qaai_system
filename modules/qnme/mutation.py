# modules/qnme/mutation.py
import random
from typing import Dict, Any, List, Tuple
import copy

def gaussian_mutate(params: Dict[str, Any], sigma: float = 0.05, float_only: bool = True) -> Dict[str, Any]:
    out = copy.deepcopy(params)
    for k, v in params.items():
        if isinstance(v, (int, float)):
            factor = 1.0 + random.gauss(0, sigma)
            newv = v * factor
            if isinstance(v, int):
                newv = max(1, int(newv))
            out[k] = newv
        elif not float_only:
            out[k] = v
    return out

def crossover(a: Dict[str, Any], b: Dict[str, Any]) -> Dict[str, Any]:
    out = {}
    keys = set(a.keys()) | set(b.keys())
    for k in keys:
        out[k] = a[k] if random.random() < 0.5 else b.get(k, a[k])
    return out

def generate_children(parents: List[Dict[str, Any]], n_children: int = 8) -> List[Dict[str, Any]]:
    children = []
    for _ in range(n_children):
        p1, p2 = random.sample(parents, 2)
        child = crossover(p1, p2)
        child = gaussian_mutate(child, sigma=0.03)
        children.append(child)
    return children
