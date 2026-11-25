"""Z3003 Module 07: Collaborative Filtering and Matrix Factorization (SVD) Recommenders."""

from __future__ import annotations

import math
import numpy as np


def cosine_user_similarity(ratings: np.ndarray) -> np.ndarray:
    """Compute centered-cosine (Pearson) user-user similarity matrix over observed entries (>0)."""
    n_users = ratings.shape[0]
    centered = np.zeros_like(ratings, dtype=float)
    for u in range(n_users):
        mask = ratings[u] > 0
        if np.any(mask):
            centered[u, mask] = ratings[u, mask] - float(np.mean(ratings[u, mask]))
    norms = np.linalg.norm(centered, axis=1, keepdims=True)
    norms = np.where(norms == 0.0, 1.0, norms)
    unit = centered / norms
    return unit @ unit.T


def predict_user_cf(ratings: np.ndarray, user: int, item: int, k: int = 2) -> float:
    """Predict rating using baseline user mean + k-nearest neighbor residual."""
    sim = cosine_user_similarity(ratings)
    user_mask = ratings[user] > 0
    mu_u = float(np.mean(ratings[user, user_mask])) if np.any(user_mask) else 3.0
    candidates: list[tuple[float, float]] = []
    for v in range(ratings.shape[0]):
        if v == user or ratings[v, item] <= 0 or sim[user, v] <= 0:
            continue
        v_mask = ratings[v] > 0
        mu_v = float(np.mean(ratings[v, v_mask]))
        candidates.append((float(sim[user, v]), float(ratings[v, item] - mu_v)))
    candidates.sort(key=lambda x: x[0], reverse=True)
    top = candidates[:k]
    if not top:
        return mu_u
    num = sum(w * diff for w, diff in top)
    den = sum(abs(w) for w, _ in top)
    return mu_u + num / den


def matrix_factorization_sgd(
    observed: list[tuple[int, int, float]],
    n_users: int,
    n_items: int,
    rank: int = 4,
    lr: float = 0.03,
    reg: float = 0.05,
    epochs: int = 120,
    seed: int = 3003,
) -> tuple[np.ndarray, np.ndarray, float, np.ndarray, np.ndarray]:
    """Fit biased latent-factor model r_hat(u,i) = mu + bu + bi + P_u . Q_i."""
    rng = np.random.default_rng(seed)
    mu = float(np.mean([r for _, _, r in observed]))
    P = rng.normal(0.0, 0.1, size=(n_users, rank))
    Q = rng.normal(0.0, 0.1, size=(n_items, rank))
    bu = np.zeros(n_users)
    bi = np.zeros(n_items)

    for _ in range(epochs):
        for u, i, r in observed:
            pred = mu + bu[u] + bi[i] + float(P[u] @ Q[i])
            err = r - pred
            bu[u] += lr * (err - reg * bu[u])
            bi[i] += lr * (err - reg * bi[i])
            p_old = P[u].copy()
            P[u] += lr * (err * Q[i] - reg * P[u])
            Q[i] += lr * (err * p_old - reg * Q[i])
    return P, Q, mu, bu, bi


def run_tests() -> None:
    R = np.array(
        [
            [5.0, 4.0, 0.0, 1.0, 0.0],
            [4.0, 5.0, 0.0, 1.0, 2.0],
            [1.0, 0.0, 5.0, 4.0, 5.0],
            [0.0, 2.0, 4.0, 5.0, 4.0],
        ]
    )
    pred_u0_i2 = predict_user_cf(R, user=0, item=2, k=2)
    pred_u2_i1 = predict_user_cf(R, user=2, item=1, k=2)
    assert pred_u2_i1 < 3.0 and 1.0 <= pred_u0_i2 <= 5.0

    obs = [(u, i, float(R[u, i])) for u in range(4) for i in range(5) if R[u, i] > 0]
    P, Q, mu, bu, bi = matrix_factorization_sgd(obs, 4, 5, rank=3, epochs=200)
    preds = np.array([mu + bu[u] + bi[i] + float(P[u] @ Q[i]) for u, i, _ in obs])
    trues = np.array([r for _, _, r in obs])
    rmse = float(np.sqrt(np.mean((preds - trues) ** 2)))
    assert rmse < 0.25
    print(f"DM07 self-tests passed (MF train RMSE={rmse:.3f}, CF pred u2_i1={pred_u2_i1:.2f}).")


if __name__ == "__main__":
    run_tests()
