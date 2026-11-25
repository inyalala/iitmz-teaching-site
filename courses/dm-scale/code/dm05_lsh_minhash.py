"""Z3003 Module 05: k-Shingling, Jaccard Similarity, MinHash Signatures, and LSH Banding."""

from __future__ import annotations

import hashlib
import random


def k_shingles(text: str, k: int = 3) -> set[str]:
    """Return the set of character k-shingles over normalized whitespace text."""
    clean = " ".join(text.lower().split())
    if len(clean) < k:
        return {clean} if clean else set()
    return {clean[i : i + k] for i in range(len(clean) - k + 1)}


def jaccard(a: set[str], b: set[str]) -> float:
    """Compute exact Jaccard similarity |A & B| / |A | B|."""
    if not a and not b:
        return 1.0
    return len(a & b) / len(a | b)


def _shingle_id(shingle: str) -> int:
    return int.from_bytes(hashlib.blake2b(shingle.encode("utf-8"), digest_size=8).digest(), "big")


class MinHashLSH:
    """MinHash signature generator and b-band x r-row LSH candidate index."""

    def __init__(self, num_hashes: int = 100, bands: int = 20, seed: int = 3003) -> None:
        if num_hashes % bands != 0:
            raise ValueError("num_hashes must be divisible by bands")
        self.num_hashes = num_hashes
        self.bands = bands
        self.rows_per_band = num_hashes // bands
        self.prime = (1 << 61) - 1
        rng = random.Random(seed)
        self.coeffs = [(rng.randrange(1, self.prime), rng.randrange(0, self.prime)) for _ in range(num_hashes)]

    def signature(self, shingles: set[str]) -> list[int]:
        ids = [_shingle_id(s) for s in shingles]
        if not ids:
            return [self.prime] * self.num_hashes
        sig = []
        for a, b in self.coeffs:
            sig.append(min((a * x + b) % self.prime for x in ids))
        return sig

    @staticmethod
    def estimated_similarity(sig_a: list[int], sig_b: list[int]) -> float:
        matches = sum(1 for x, y in zip(sig_a, sig_b) if x == y)
        return matches / len(sig_a)

    def candidate_pairs(self, docs: dict[str, set[str]]) -> set[tuple[str, str]]:
        sigs = {doc_id: self.signature(sh) for doc_id, sh in docs.items()}
        candidates: set[tuple[str, str]] = set()
        for band_idx in range(self.bands):
            lo = band_idx * self.rows_per_band
            hi = lo + self.rows_per_band
            buckets: dict[tuple[int, ...], list[str]] = {}
            for doc_id, sig in sigs.items():
                key = tuple(sig[lo:hi])
                buckets.setdefault(key, []).append(doc_id)
            for members in buckets.values():
                if len(members) > 1:
                    members_sorted = sorted(members)
                    for i in range(len(members_sorted)):
                        for j in range(i + 1, len(members_sorted)):
                            candidates.add((members_sorted[i], members_sorted[j]))
        return candidates


def s_curve_probability(sim: float, bands: int, rows: int) -> float:
    """Theoretical probability 1 - (1 - s^r)^b that two docs become an LSH candidate."""
    return 1.0 - (1.0 - sim ** rows) ** bands


def run_tests() -> None:
    docs_text = {
        "d1": "zanzibar clove harvest in pemba north during masika rains",
        "d2": "zanzibar clove harvest in pemba south during masika rains",
        "d3": "apache spark mapreduce word count on distributed cluster nodes",
        "d4": "apache spark mapreduce log analysis on distributed cluster nodes",
    }
    shingles = {k: k_shingles(v, k=3) for k, v in docs_text.items()}
    j12 = jaccard(shingles["d1"], shingles["d2"])
    j13 = jaccard(shingles["d1"], shingles["d3"])
    assert j12 > 0.65 and j13 < 0.15

    lsh = MinHashLSH(num_hashes=100, bands=20, seed=3003)
    s1 = lsh.signature(shingles["d1"])
    s2 = lsh.signature(shingles["d2"])
    est12 = lsh.estimated_similarity(s1, s2)
    assert abs(est12 - j12) < 0.12

    cands = lsh.candidate_pairs(shingles)
    assert ("d1", "d2") in cands and ("d3", "d4") in cands and ("d1", "d3") not in cands
    assert s_curve_probability(0.8, 20, 5) > 0.999
    assert s_curve_probability(0.2, 20, 5) < 0.01
    print(f"DM05 self-tests passed (Jaccard(d1,d2)={j12:.3f}, MinHash est={est12:.3f}, LSH candidates={sorted(cands)}).")


if __name__ == "__main__":
    run_tests()
