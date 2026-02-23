"""
strategies/adapters/auto_wrappers.py

Helpers to auto-wrap strategy modules that require complex constructor args.
Generates thin wrapper files into strategies/_wrappers/.
"""
from pathlib import Path
import importlib.util
import inspect
import types
import pandas as pd
import traceback

WRAP_OUTPUT_DIR = Path("strategies") / "_wrappers"
WRAP_OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

def load_module_from_path(path: Path):
    spec = importlib.util.spec_from_file_location(path.stem, str(path))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m

def try_instantiate_class(cls):
    try:
        return cls()
    except Exception:
        pass
    try:
        sig = inspect.signature(cls.__init__)
    except Exception:
        sig = None
    if sig:
        params = list(sig.parameters.values())[1:]
        kwargs = {}
        for p in params:
            if p.default is not inspect._empty:
                continue
            # provide conservative dummy values
            name = p.name.lower()
            if "screen" in name or "result" in name:
                kwargs[p.name] = []
            elif name in ("config","cfg","settings"):
                kwargs[p.name] = {}
            elif name in ("ctx","context"):
                ctx = types.SimpleNamespace()
                ctx.now = pd.Timestamp.utcnow()
                ctx.market = {}
                ctx.engine = types.SimpleNamespace(build_features=lambda ctx,sym: pd.DataFrame({"close":[100.0]}, index=[ctx.now]))
                kwargs[p.name] = ctx
            else:
                kwargs[p.name] = None
        try:
            return cls(**kwargs)
        except Exception:
            pass
    return None

def build_wrapper(module_path: str, write_file: bool = True):
    p = Path(module_path)
    if not p.exists():
        raise FileNotFoundError(module_path)
    mod = load_module_from_path(p)
    # if module already exposes generate_signals, we don't need a wrapper
    if hasattr(mod, "generate_signals") and inspect.isfunction(getattr(mod, "generate_signals")):
        return mod

    # find any class with generate_signals
    for _, cls in inspect.getmembers(mod, inspect.isclass):
        if hasattr(cls, "generate_signals"):
            inst = try_instantiate_class(cls)
            if inst is not None:
                # produce simple module-like object that calls the instance
                return types.SimpleNamespace(generate_signals=lambda ctx, _inst=inst: _inst.generate_signals(ctx))
            else:
                # create a safe wrapper module file that tries to call common constructor forms
                wrapper_name = f"{p.stem}_wrapper.py"
                outp = WRAP_OUTPUT_DIR / wrapper_name
                code = (
f"# Auto-generated wrapper for {p.name}\n"
"import importlib\n"
"mod = importlib.import_module('strategies." + p.stem + "')\n\n"
"def generate_signals(ctx):\n"
"    # Try top-level function first\n"
"    try:\n"
"        if hasattr(mod, 'generate_signals'):\n"
"            return mod.generate_signals(ctx)\n"
"    except Exception:\n"
"        pass\n"
"    # Try to find a class with generate_signals and try common constructor forms\n"
"    try:\n"
"        import inspect\n"
"        for _, cls in inspect.getmembers(mod, inspect.isclass):\n"
"            if hasattr(cls, 'generate_signals'):\n"
"                try:\n"
"                    # try no-arg\n"
"                    inst = cls()\n"
"                    return inst.generate_signals(ctx)\n"
"                except Exception:\n"
"                    try:\n"
"                        # try single-list arg\n"
"                        inst = cls([])\n"
"                        return inst.generate_signals(ctx)\n"
"                    except Exception:\n"
"                        continue\n"
"    except Exception:\n"
"        return None\n"
"    return None\n"
                )
                outp.write_text(code)
                return load_module_from_path(outp)

    # no candidate found: return noop module
    return types.SimpleNamespace(generate_signals=lambda ctx: None)

if __name__ == "__main__":
    base = Path("strategies")
    for p in base.glob("*.py"):
        if p.name.startswith("_") or p.name == "strategy_engine.py":
            continue
        try:
            w = build_wrapper(str(p), write_file=True)
            print("Wrapped", p.name)
        except Exception as e:
            print("Failed to wrap", p.name, e)
