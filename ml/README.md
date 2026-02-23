# ML / Online model conventions

This small README documents the lightweight API conventions for online models used across the platform.

## Expected methods

- `predict_one(x: dict) -> float` or `predict_proba_one(x: dict) -> dict/float`  
- `learn_one(x: dict, y: int|float) -> None` or `partial_fit(X, y)` for batch wrappers
- Optional: `save(path)` / `load(path)`

## Wrapping scikit / river
- River-style models implement `learn_one` and `predict_proba_one`.
- Scikit-style incremental models can be wrapped with an adapter that exposes `learn_one` and `predict_one`.

## Versioning & Registry
- Model metadata: name, version, created_ts, features, hyperparams.
- Use model name + version for atomic swaps. Keep warmup copies before swap.

## Testing
- Add a smoke test that ensures `predict_one` and `learn_one` run on a tiny input.
- Add an integration test for the retrain endpoint (if present) that runs in dockerized CI.

