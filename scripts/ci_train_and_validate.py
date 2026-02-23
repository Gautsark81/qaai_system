# scripts/ci_train_and_validate.py
"""
Train a tiny meta-model on synthetic data and assert saved model can load and predict.
Used by CI to validate the meta-model pipeline.
"""
import numpy as np
from modules.meta.model import MetaModel

def main():
    # synthetic
    rng = np.random.RandomState(0)
    X = rng.randn(200, 6)
    y = (X[:, 0] > 0.7).astype(int)  # 1 else 0
    # map 0 to 0, 1 to 1, -1 not present but model supports it; for training we map to {0,1}
    # adapt labels to {1, -1, 0} by injecting some -1s
    y2 = np.where(X[:, 0] < -0.7, -1, np.where(X[:, 0] > 0.7, 1, 0))
    mm = MetaModel(n_estimators=10)
    stats = mm.fit(X, y2)
    print("Trained meta-model stats:", stats)
    mm.save("build/ci_meta_model.joblib")
    mm2 = MetaModel(n_estimators=1)
    mm2.load("build/ci_meta_model.joblib")
    out = mm2.predict_proba(X[0])
    print("Sample prediction:", out)

if __name__ == "__main__":
    main()
