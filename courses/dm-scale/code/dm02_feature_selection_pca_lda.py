"""Z3003 Module 02: Information Gain Feature Selection, Leakage-Safe Scaling, PCA, and Fisher LDA."""

from __future__ import annotations

import math
from collections import Counter
from typing import Any

import numpy as np


def entropy(labels: list[Any]) -> float:
    """Compute Shannon entropy H(S) in bits."""
    n = len(labels)
    if n == 0:
        return 0.0
    counts = Counter(labels)
    return -sum((c / n) * math.log2(c / n) for c in counts.values() if c > 0)


def information_gain_categorical(feature: list[Any], labels: list[Any]) -> float:
    """Compute IG(S, A) = H(S) - sum_v (|S_v| / |S|) H(S_v)."""
    n = len(labels)
    base_h = entropy(labels)
    groups: dict[Any, list[Any]] = {}
    for val, lbl in zip(feature, labels):
        groups.setdefault(val, []).append(lbl)
    after_h = sum((len(sub) / n) * entropy(sub) for sub in groups.values())
    return base_h - after_h


def best_numeric_threshold_ig(values: np.ndarray, labels: np.ndarray) -> tuple[float, float]:
    """Find midpoint split threshold maximizing Information Gain."""
    order = np.argsort(values)
    sv, sl = values[order], labels[order]
    base_h = entropy(sl.tolist())
    best_thresh, best_ig = float(sv[0]), -1.0
    n = len(sl)
    for i in range(n - 1):
        if sv[i] == sv[i + 1]:
            continue
        t = 0.5 * float(sv[i] + sv[i + 1])
        left = sl[: i + 1].tolist()
        right = sl[i + 1 :].tolist()
        w_h = (len(left) / n) * entropy(left) + (len(right) / n) * entropy(right)
        ig = base_h - w_h
        if ig > best_ig:
            best_ig, best_thresh = ig, t
    return best_thresh, best_ig


def fit_transform_zscore(X_train: np.ndarray, X_test: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """Leakage-free standardization fitted strictly on X_train."""
    mu = np.mean(X_train, axis=0)
    sd = np.where(np.std(X_train, axis=0) == 0, 1.0, np.std(X_train, axis=0))
    return (X_train - mu) / sd, (X_test - mu) / sd


def robust_zscore(x: np.ndarray) -> np.ndarray:
    """Iglewicz-Hoaglin modified z-score: 0.6745 * (x - median) / MAD."""
    med = float(np.median(x))
    mad = float(np.median(np.abs(x - med)))
    if mad == 0.0:
        return np.zeros_like(x, dtype=float)
    return 0.6745 * (x - med) / mad


def pca_fit_transform(X_std: np.ndarray, k: int) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    """Compute top-k principal components via symmetric eigendecomposition of covariance matrix."""
    cov = np.cov(X_std, rowvar=False, ddof=1)
    eigvals, eigvecs = np.linalg.eigh(cov)
    idx = np.argsort(eigvals)[::-1]
    eigvals = eigvals[idx]
    eigvecs = eigvecs[:, idx]
    explained_ratio = eigvals / np.sum(eigvals)
    components = eigvecs[:, :k]
    return X_std @ components, eigvals[:k], explained_ratio


def fisher_lda_binary(X: np.ndarray, y: np.ndarray) -> np.ndarray:
    """Compute 1D Fisher Linear Discriminant projection vector w maximizing between/within scatter."""
    classes = np.unique(y)
    if len(classes) != 2:
        raise ValueError("fisher_lda_binary expects exactly 2 classes")
    X0, X1 = X[y == classes[0]], X[y == classes[1]]
    m0, m1 = np.mean(X0, axis=0), np.mean(X1, axis=0)
    Sw = (X0 - m0).T @ (X0 - m0) + (X1 - m1).T @ (X1 - m1) + 1e-6 * np.eye(X.shape[1])
    w = np.linalg.solve(Sw, m1 - m0)
    return w / np.linalg.norm(w)


def run_tests() -> None:
    # Lecture 7 rainfall split: 8 farms L L L H H H H L
    rain = np.array([1000, 1100, 1200, 1300, 1400, 1500, 1600, 1700], dtype=float)
    y = np.array(["L", "L", "L", "H", "H", "H", "H", "L"])
    t, ig = best_numeric_threshold_ig(rain, y)
    assert abs(t - 1250.0) < 1e-6 and abs(ig - 0.549) < 0.01

    # Lecture 8 2x2 covariance matrix [[2, 1], [1, 2]] -> eigenvalues 3, 1 (75%, 25%)
    cov = np.array([[2.0, 1.0], [1.0, 2.0]])
    vals, _ = np.linalg.eigh(cov)
    vals = np.sort(vals)[::-1]
    assert abs(vals[0] - 3.0) < 1e-9 and abs(vals[1] - 1.0) < 1e-9

    rng = np.random.default_rng(42)
    X_tr = rng.normal(size=(200, 4))
    X_te = rng.normal(size=(50, 4))
    Z_tr, Z_te = fit_transform_zscore(X_tr, X_te)
    proj, evals, ratio = pca_fit_transform(Z_tr, k=2)
    assert proj.shape == (200, 2) and abs(np.sum(ratio) - 1.0) < 1e-9

    X_lda = np.vstack([rng.normal([0, 0], 0.5, (40, 2)), rng.normal([3, 3], 0.5, (40, 2))])
    y_lda = np.array([0] * 40 + [1] * 40)
    w = fisher_lda_binary(X_lda, y_lda)
    assert abs(np.linalg.norm(w) - 1.0) < 1e-9
    print(f"DM02 self-tests passed (best rainfall split={t:.0f} mm, IG={ig:.3f}).")


if __name__ == "__main__":
    run_tests()
