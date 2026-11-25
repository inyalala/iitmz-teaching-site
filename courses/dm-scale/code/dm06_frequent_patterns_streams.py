"""Z3003 Module 06: Apriori Frequent Itemsets, Null-Invariant Rule Evaluation, and Bloom Filters."""

from __future__ import annotations

from itertools import combinations
import hashlib
import math
from typing import Any, FrozenSet


def apriori(transactions: list[set[str]], min_support: float) -> dict[FrozenSet[str], int]:
    """Find all frequent itemsets with support >= min_support using Apriori pruning."""
    n = len(transactions)
    min_count = math.ceil(min_support * n)
    counts: dict[str, int] = {}
    for basket in transactions:
        for item in basket:
            counts[item] = counts.get(item, 0) + 1
    freq: dict[FrozenSet[str], int] = {
        frozenset([item]): cnt for item, cnt in counts.items() if cnt >= min_count
    }
    current_l = sorted(freq.keys(), key=lambda fs: sorted(fs))
    k = 2
    while current_l:
        prev_set = set(current_l)
        candidates: set[FrozenSet[str]] = set()
        for i in range(len(current_l)):
            for j in range(i + 1, len(current_l)):
                u = current_l[i] | current_l[j]
                if len(u) == k and all(frozenset(sub) in prev_set for sub in combinations(u, k - 1)):
                    candidates.add(u)
        if not candidates:
            break
        c_counts: dict[FrozenSet[str], int] = {c: 0 for c in candidates}
        for basket in transactions:
            for c in candidates:
                if c.issubset(basket):
                    c_counts[c] += 1
        next_l = [c for c, cnt in c_counts.items() if cnt >= min_count]
        for c in next_l:
            freq[c] = c_counts[c]
        current_l = sorted(next_l, key=lambda fs: sorted(fs))
        k += 1
    return freq


def evaluate_rule(
    freq_counts: dict[FrozenSet[str], int],
    n_baskets: int,
    ante: FrozenSet[str],
    cons: FrozenSet[str],
) -> dict[str, float]:
    """Compute support, confidence, lift, Kulczynski, and Imbalance Ratio for ante -> cons."""
    both = freq_counts[ante | cons]
    ca = freq_counts[ante]
    cb = freq_counts[cons]
    sup = both / n_baskets
    conf = both / ca
    lift = conf / (cb / n_baskets)
    kulc = 0.5 * ((both / ca) + (both / cb))
    ir = abs(ca - cb) / (ca + cb - both)
    return {"support": sup, "confidence": conf, "lift": lift, "kulczynski": kulc, "imbalance_ratio": ir}


class BloomFilter:
    """Space-efficient probabilistic set membership filter with k independent hashes."""

    def __init__(self, m_bits: int, k_hashes: int) -> None:
        self.m = m_bits
        self.k = k_hashes
        self.bits = bytearray(m_bits)

    def _positions(self, item: str) -> list[int]:
        pos = []
        for salt in range(self.k):
            digest = hashlib.blake2b(f"{salt}:{item}".encode("utf-8"), digest_size=8).digest()
            pos.append(int.from_bytes(digest, "big") % self.m)
        return pos

    def add(self, item: str) -> None:
        for p in self._positions(item):
            self.bits[p] = 1

    def contains(self, item: str) -> bool:
        return all(self.bits[p] == 1 for p in self._positions(item))


def run_tests() -> None:
    # Classroom 9 agro-dealer baskets (Week 5 Summary)
    baskets = [
        {"R", "U", "H"},
        {"R", "U", "H"},
        {"R", "U", "S"},
        {"R", "U", "S"},
        {"R", "S"},
        {"R", "S"},
        {"U", "S", "P"},
        {"U", "P"},
        {"U", "S"},
    ]
    freq = apriori(baskets, min_support=2 / 9)
    assert len(freq) == 13
    assert freq[frozenset({"H", "R", "U"})] == 2 and freq[frozenset({"R", "S", "U"})] == 2

    # Decoy popular item test: 'hoe' appears in 80% of synthetic baskets
    b2 = [{"rice_seed", "urea", "hoe"} for _ in range(30)] + [{"hoe"} for _ in range(60)] + [{"rice_seed", "urea"} for _ in range(10)]
    f2 = apriori(b2, min_support=0.25)
    m_urea = evaluate_rule(f2, len(b2), frozenset({"rice_seed"}), frozenset({"urea"}))
    m_hoe = evaluate_rule(f2, len(b2), frozenset({"rice_seed"}), frozenset({"hoe"}))
    assert m_urea["lift"] > 2.0 and m_hoe["lift"] < 1.0

    # Bloom filter zero false negatives + low false-positive rate
    bf = BloomFilter(m_bits=4096, k_hashes=5)
    seen = [f"farm_{i}" for i in range(400)]
    for s in seen:
        bf.add(s)
    assert all(bf.contains(s) for s in seen)
    fps = sum(1 for i in range(400, 1400) if bf.contains(f"farm_{i}"))
    assert fps / 1000 < 0.05
    print(f"DM06 self-tests passed (Apriori itemsets={len(freq)}, Bloom FP rate={fps/1000:.3f}).")


if __name__ == "__main__":
    run_tests()
