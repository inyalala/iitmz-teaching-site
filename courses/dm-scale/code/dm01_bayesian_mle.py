"""Z3003 Module 01: Bayesian Decision Theory, MLE, and Naive Bayes Classification."""

from __future__ import annotations

import math
from collections import Counter, defaultdict
from typing import Any

import numpy as np


def bernoulli_mle(outcomes: list[int]) -> float:
    """Return Maximum Likelihood Estimate p_hat = mean(outcomes)."""
    if not outcomes:
        raise ValueError("outcomes must be non-empty")
    return sum(outcomes) / len(outcomes)


def gaussian_mle(values: np.ndarray) -> tuple[float, float]:
    """Return (mu_hat, sigma_hat) MLE parameters for a 1D numeric array."""
    mu = float(np.mean(values))
    var = float(np.mean((values - mu) ** 2))
    return mu, math.sqrt(max(var, 1e-12))


class CategoricalNaiveBayes:
    """Discrete Naive Bayes classifier with Laplace smoothing in log-probability space."""

    def __init__(self, alpha: float = 1.0) -> None:
        self.alpha = alpha
        self.classes_: list[Any] = []
        self.class_log_prior_: dict[Any, float] = {}
        self.feature_log_prob_: dict[tuple[Any, int, Any], float] = {}
        self.categories_: dict[int, set[Any]] = defaultdict(set)
        self.class_counts_: Counter[Any] = Counter()

    def fit(self, X: list[list[Any]], y: list[Any]) -> CategoricalNaiveBayes:
        n = len(y)
        self.class_counts_ = Counter(y)
        self.classes_ = sorted(self.class_counts_.keys(), key=str)
        n_features = len(X[0])
        val_counts: dict[tuple[Any, int], Counter[Any]] = defaultdict(Counter)

        for row, label in zip(X, y):
            for j, val in enumerate(row):
                self.categories_[j].add(val)
                val_counts[(label, j)][val] += 1

        for c in self.classes_:
            self.class_log_prior_[c] = math.log(self.class_counts_[c] / n)
            for j in range(n_features):
                k_j = len(self.categories_[j])
                denom = self.class_counts_[c] + self.alpha * k_j
                for val in self.categories_[j]:
                    num = val_counts[(c, j)][val] + self.alpha
                    self.feature_log_prob_[(c, j, val)] = math.log(num / denom)
        return self

    def predict_proba(self, row: list[Any]) -> dict[Any, float]:
        log_scores: dict[Any, float] = {}
        for c in self.classes_:
            score = self.class_log_prior_[c]
            for j, val in enumerate(row):
                if (c, j, val) in self.feature_log_prob_:
                    score += self.feature_log_prob_[(c, j, val)]
                else:
                    k_j = len(self.categories_[j]) + 1
                    score += math.log(self.alpha / (self.class_counts_[c] + self.alpha * k_j))
            log_scores[c] = score
        max_s = max(log_scores.values())
        exp_scores = {c: math.exp(s - max_s) for c, s in log_scores.items()}
        total = sum(exp_scores.values())
        return {c: v / total for c, v in exp_scores.items()}

    def predict(self, X: list[list[Any]]) -> list[Any]:
        return [max(self.predict_proba(r).items(), key=lambda kv: kv[1])[0] for r in X]


class GaussianNaiveBayes:
    """Gaussian Naive Bayes fitted by per-class MLE mean and variance."""

    def __init__(self) -> None:
        self.classes_: list[Any] = []
        self.priors_: dict[Any, float] = {}
        self.params_: dict[Any, tuple[np.ndarray, np.ndarray]] = {}

    def fit(self, X: np.ndarray, y: np.ndarray) -> GaussianNaiveBayes:
        self.classes_ = list(np.unique(y))
        n = len(y)
        for c in self.classes_:
            Xc = X[y == c]
            self.priors_[c] = len(Xc) / n
            mu = np.mean(Xc, axis=0)
            var = np.var(Xc, axis=0) + 1e-9
            self.params_[c] = (mu, var)
        return self

    def predict(self, X: np.ndarray) -> np.ndarray:
        preds = []
        for x in X:
            best_c, best_lp = None, -float("inf")
            for c in self.classes_:
                mu, var = self.params_[c]
                ll = -0.5 * np.sum(np.log(2.0 * math.pi * var) + ((x - mu) ** 2) / var)
                lp = math.log(self.priors_[c]) + float(ll)
                if lp > best_lp:
                    best_lp = lp
                    best_c = c
            preds.append(best_c)
        return np.array(preds)


def run_tests() -> None:
    assert abs(bernoulli_mle([1, 1, 0, 1, 1, 1, 1, 1, 1, 0]) - 0.8) < 1e-9
    # Lecture 17 Zanzibar farm toy table (14 farms)
    X_cat = [
        ["Low", "No", "No"], ["Low", "No", "Yes"], ["Med", "No", "No"], ["High", "Yes", "No"],
        ["High", "Yes", "Yes"], ["High", "No", "Yes"], ["Med", "Yes", "Yes"], ["Low", "Yes", "No"],
        ["Low", "No", "No"], ["High", "No", "No"], ["Low", "Yes", "Yes"], ["Med", "Yes", "No"],
        ["Med", "No", "Yes"], ["High", "Yes", "Yes"],
    ]
    y_cat = ["Low", "Low", "High", "High", "High", "Low", "High", "Low", "High", "High", "High", "High", "High", "Low"]
    nb = CategoricalNaiveBayes(alpha=1.0).fit(X_cat, y_cat)
    probs = nb.predict_proba(["High", "Yes", "No"])
    assert abs(sum(probs.values()) - 1.0) < 1e-9 and probs["High"] > probs["Low"]

    rng = np.random.default_rng(3003)
    X0 = rng.normal(loc=[1150.0, 0.8], scale=[120.0, 0.3], size=(120, 2))
    X1 = rng.normal(loc=[1520.0, 2.4], scale=[120.0, 0.5], size=(120, 2))
    Xg = np.vstack([X0, X1])
    yg = np.array([0] * 120 + [1] * 120)
    gnb = GaussianNaiveBayes().fit(Xg, yg)
    acc = float(np.mean(gnb.predict(Xg) == yg))
    assert acc > 0.93
    print(f"DM01 self-tests passed (GaussianNB synthetic farm accuracy = {acc:.3f}).")


if __name__ == "__main__":
    run_tests()
