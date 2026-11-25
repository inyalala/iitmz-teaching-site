"""Z3003 Module 09: Stream Sketches (Flajolet-Martin Distinct Count, AMS F2 Moment, and DGIM)."""

from __future__ import annotations

import hashlib
import math
import random


def _trailing_zeros(x: int) -> int:
    if x == 0:
        return 32
    tz = 0
    while (x & 1) == 0:
        tz += 1
        x >>= 1
    return tz


def flajolet_martin_estimate(stream: list[str], num_hashes: int = 32, seed: int = 3003) -> float:
    """Estimate distinct items F0 using median-of-group-means Flajolet-Martin trailing zeros."""
    rng = random.Random(seed)
    max_tz = [0] * num_hashes
    salts = [rng.randint(1, 10**9) for _ in range(num_hashes)]
    for item in stream:
        for idx, salt in enumerate(salts):
            h = int.from_bytes(hashlib.blake2b(f"{salt}:{item}".encode(), digest_size=8).digest(), "big")
            max_tz[idx] = max(max_tz[idx], _trailing_zeros(h))
    ests = [2 ** r for r in max_tz]
    # Group into 4 groups of 8, average per group, take median
    groups = [sum(ests[i : i + 8]) / 8.0 for i in range(0, num_hashes, 8)]
    groups.sort()
    return 0.5 * (groups[len(groups) // 2 - 1] + groups[len(groups) // 2])


def ams_second_moment(stream: list[str], num_samples: int = 200, seed: int = 3003) -> float:
    """Alon-Matias-Szegedy (AMS) estimate of F2 = sum_x count(x)^2 using O(num_samples) memory."""
    rng = random.Random(seed)
    n = len(stream)
    positions = sorted(rng.randrange(n) for _ in range(num_samples))
    tracked: list[tuple[str, int]] = []  # [element, count_from_pos]
    pos_idx = 0
    counts: list[int] = []
    elems: list[str] = []
    for t, item in enumerate(stream):
        for idx, el in enumerate(elems):
            if el == item:
                counts[idx] += 1
        while pos_idx < len(positions) and positions[pos_idx] == t:
            elems.append(item)
            counts.append(1)
            pos_idx += 1
    ests = [n * (2 * c - 1) for c in counts]
    return sum(ests) / len(ests)


class DGIMWindow:
    """Sliding-window 1-bit counter storing O(log^2 N) exponentially sized buckets."""

    def __init__(self, window_size: int) -> None:
        self.N = window_size
        self.t = 0
        self.buckets: list[tuple[int, int]] = []  # (timestamp, size), newest first

    def add_bit(self, bit: int) -> None:
        self.t += 1
        while self.buckets and self.buckets[-1][0] <= self.t - self.N:
            self.buckets.pop()
        if bit == 1:
            self.buckets.insert(0, (self.t, 1))
            self._merge()

    def _merge(self) -> None:
        i = 0
        while i + 2 < len(self.buckets):
            if self.buckets[i][1] == self.buckets[i + 1][1] == self.buckets[i + 2][1]:
                ts = max(self.buckets[i + 1][0], self.buckets[i + 2][0])
                sz = self.buckets[i + 1][1] * 2
                self.buckets[i + 1 : i + 3] = [(ts, sz)]
            else:
                i += 1

    def estimate_ones(self) -> float:
        if not self.buckets:
            return 0.0
        total = sum(sz for _, sz in self.buckets[:-1])
        return total + 0.5 * self.buckets[-1][1]


def run_tests() -> None:
    rng = random.Random(3003)
    stream = [f"farm_{rng.randint(1, 500)}" for _ in range(3000)]
    true_f0 = len(set(stream))
    est_f0 = flajolet_martin_estimate(stream)
    assert 0.4 * true_f0 <= est_f0 <= 2.5 * true_f0

    freq: dict[str, int] = {}
    for x in stream:
        freq[x] = freq.get(x, 0) + 1
    true_f2 = sum(c * c for c in freq.values())
    est_f2 = ams_second_moment(stream, num_samples=250)
    assert abs(est_f2 - true_f2) / true_f2 < 0.35

    bits = [rng.choice([0, 1, 1]) for _ in range(300)]
    dgim = DGIMWindow(window_size=64)
    for b in bits:
        dgim.add_bit(b)
    true_ones = sum(bits[-64:])
    est_ones = dgim.estimate_ones()
    assert abs(est_ones - true_ones) <= 0.5 * true_ones
    print(f"DM09 self-tests passed (F0 true={true_f0}/est={est_f0:.0f}, F2 err={abs(est_f2-true_f2)/true_f2:.1%}, DGIM {est_ones:.1f} vs {true_ones}).")


if __name__ == "__main__":
    run_tests()
