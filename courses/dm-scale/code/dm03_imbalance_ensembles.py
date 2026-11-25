"""Z3003 Module 03: Class Imbalance Metrics, Oversampling, Bagging, Random Forest, and AdaBoost."""

from __future__ import annotations

import math
import numpy as np
from sklearn.ensemble import BaggingClassifier, GradientBoostingClassifier, RandomForestClassifier
from sklearn.model_selection import StratifiedKFold, cross_val_score
from sklearn.tree import DecisionTreeClassifier


def binary_metrics(y_true: np.ndarray, y_pred: np.ndarray) -> dict[str, float]:
    """Return accuracy, precision, recall, F1, and MCC for binary {0, 1} labels."""
    tp = int(np.sum((y_true == 1) & (y_pred == 1)))
    tn = int(np.sum((y_true == 0) & (y_pred == 0)))
    fp = int(np.sum((y_true == 0) & (y_pred == 1)))
    fn = int(np.sum((y_true == 1) & (y_pred == 0)))
    acc = (tp + tn) / max(1, tp + tn + fp + fn)
    prec = tp / max(1, tp + fp)
    rec = tp / max(1, tp + fn)
    f1 = 2 * prec * rec / max(1e-12, prec + rec)
    denom = math.sqrt((tp + fp) * (tp + fn) * (tn + fp) * (tn + fn))
    mcc = (tp * tn - fp * fn) / denom if denom > 0 else 0.0
    return {"accuracy": acc, "precision": prec, "recall": rec, "f1": f1, "mcc": mcc}


def smote_interpolate(X_minority: np.ndarray, n_new: int, k: int = 5, seed: int = 42) -> np.ndarray:
    """Generate synthetic minority samples via k-nearest-neighbor linear interpolation."""
    rng = np.random.default_rng(seed)
    m = len(X_minority)
    k = min(k, max(1, m - 1))
    synthetic = np.zeros((n_new, X_minority.shape[1]))
    for idx in range(n_new):
        i = int(rng.integers(0, m))
        dists = np.linalg.norm(X_minority - X_minority[i], axis=1)
        nbrs = np.argsort(dists)[1 : k + 1]
        j = int(rng.choice(nbrs))
        lam = float(rng.random())
        synthetic[idx] = X_minority[i] + lam * (X_minority[j] - X_minority[i])
    return synthetic


class SimpleAdaBoost:
    """Binary AdaBoost using 1-level Decision Stumps on labels {-1, +1}."""

    def __init__(self, n_estimators: int = 25) -> None:
        self.n_estimators = n_estimators
        self.stumps: list[DecisionTreeClassifier] = []
        self.alphas: list[float] = []

    def fit(self, X: np.ndarray, y01: np.ndarray) -> SimpleAdaBoost:
        n = len(y01)
        y = np.where(y01 == 1, 1.0, -1.0)
        w = np.full(n, 1.0 / n)
        self.stumps, self.alphas = [], []
        for _ in range(self.n_estimators):
            stump = DecisionTreeClassifier(max_depth=1, random_state=0)
            stump.fit(X, y01, sample_weight=w)
            pred = np.where(stump.predict(X) == 1, 1.0, -1.0)
            err = float(np.sum(w[pred != y]))
            err = min(max(err, 1e-8), 1.0 - 1e-8)
            alpha = 0.5 * math.log((1.0 - err) / err)
            w *= np.exp(-alpha * y * pred)
            w /= np.sum(w)
            self.stumps.append(stump)
            self.alphas.append(alpha)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        margin = np.zeros(len(X))
        for stump, alpha in zip(self.stumps, self.alphas):
            margin += alpha * np.where(stump.predict(X) == 1, 1.0, -1.0)
        return (margin >= 0).astype(int)


def run_tests() -> None:
    rng = np.random.default_rng(3003)
    X_maj = rng.normal(0.0, 1.0, size=(360, 4))
    X_min = rng.normal(1.8, 0.9, size=(40, 4))
    X = np.vstack([X_maj, X_min])
    y = np.array([0] * 360 + [1] * 40)

    # Always-0 baseline: 90% accuracy, 0 recall!
    m_zero = binary_metrics(y, np.zeros_like(y))
    assert abs(m_zero["accuracy"] - 0.90) < 1e-9 and m_zero["recall"] == 0.0

    # Oversampling via SMOTE interpolation
    X_syn = smote_interpolate(X_min, n_new=160, k=5)
    X_bal = np.vstack([X, X_syn])
    y_bal = np.concatenate([y, np.ones(160, dtype=int)])

    ada = SimpleAdaBoost(n_estimators=20).fit(X_bal, y_bal)
    m_ada = binary_metrics(y, ada.predict(X))
    assert m_ada["recall"] > 0.70 and m_ada["f1"] > 0.60

    cv = StratifiedKFold(n_splits=4, shuffle=True, random_state=7)
    rf = RandomForestClassifier(n_estimators=40, random_state=7)
    gb = GradientBoostingClassifier(n_estimators=40, random_state=7)
    bag = BaggingClassifier(n_estimators=25, random_state=7)
    for model in (rf, gb, bag):
        scores = cross_val_score(model, X, y, cv=cv, scoring="f1")
        assert scores.mean() > 0.65
    print(f"DM03 self-tests passed (AdaBoost F1={m_ada['f1']:.3f}, recall={m_ada['recall']:.3f}).")


if __name__ == "__main__":
    run_tests()
