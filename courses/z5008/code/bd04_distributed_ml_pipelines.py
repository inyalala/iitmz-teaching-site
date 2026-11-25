"""Z5008 Lab Module 04: Distributed ML Pipeline & Experiment Tracking Registry."""

from __future__ import annotations

import json
import numpy as np
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import f1_score, roc_auc_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler


def run_ml_experiment(c_reg: float, seed: int = 5008) -> dict[str, float]:
    """Train leakage-free Pipeline and return logged parameters and evaluation metrics."""
    rng = np.random.default_rng(seed)
    X_neg = rng.normal([0.0, 0.0, 1.0], 1.0, size=(320, 3))
    X_pos = rng.normal([1.7, 1.5, 2.2], 0.9, size=(80, 3))
    X = np.vstack([X_neg, X_pos])
    y = np.array([0] * 320 + [1] * 80)
    X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.25, stratify=y, random_state=seed)

    pipe = Pipeline([("scaler", StandardScaler()), ("clf", LogisticRegression(C=c_reg, max_iter=500))])
    pipe.fit(X_tr, y_tr)
    probs = pipe.predict_proba(X_te)[:, 1]
    preds = (probs >= 0.5).astype(int)
    return {
        "C": c_reg,
        "f1": float(f1_score(y_te, preds)),
        "roc_auc": float(roc_auc_score(y_te, probs)),
    }


def run_tests() -> None:
    runs = [run_ml_experiment(c) for c in (0.1, 1.0, 10.0)]
    best = max(runs, key=lambda r: r["roc_auc"])
    assert best["roc_auc"] > 0.90 and best["f1"] > 0.75
    print(f"BD04 self-tests passed (best run: {json.dumps(best)}).")


if __name__ == "__main__":
    run_tests()
