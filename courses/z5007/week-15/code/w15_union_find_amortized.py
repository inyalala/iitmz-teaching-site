"""Week 15 Reference Module: Disjoint Set Union (Union-Find) and Amortized Potential Analysis."""

from __future__ import annotations


class DisjointSetUnion:
    """Union-Find with path compression and union by size/rank."""

    def __init__(self, n: int) -> None:
        self.parent = list(range(n))
        self.size = [1] * n
        self.components = n
        self.parent_hops = 0

    def find(self, x: int) -> int:
        root = x
        while self.parent[root] != root:
            root = self.parent[root]
            self.parent_hops += 1
        while self.parent[x] != root:
            nxt = self.parent[x]
            self.parent[x] = root
            x = nxt
        return root

    def union(self, a: int, b: int) -> bool:
        ra, rb = self.find(a), self.find(b)
        if ra == rb:
            return False
        if self.size[ra] < self.size[rb]:
            ra, rb = rb, ra
        self.parent[rb] = ra
        self.size[ra] += self.size[rb]
        self.components -= 1
        return True


def binary_counter_potential_trace(increments: int) -> tuple[int, int]:
    """Simulate a k-bit binary counter; return (total_bit_flips, final_potential_ones)."""
    bits = [0] * 32
    flips = 0
    for _ in range(increments):
        i = 0
        while bits[i] == 1:
            bits[i] = 0
            flips += 1
            i += 1
        bits[i] = 1
        flips += 1
    return flips, sum(bits)


def run_tests() -> None:
    dsu = DisjointSetUnion(1000)
    for i in range(999):
        assert dsu.union(i, i + 1)
    assert dsu.components == 1
    for _ in range(5000):
        assert dsu.find(999) == dsu.find(0)
    avg_hops = dsu.parent_hops / 7000
    assert avg_hops < 1.5

    flips, phi = binary_counter_potential_trace(1024)
    # Amortized bound: flips + phi <= 2 * increments
    assert flips < 2 * 1024 and phi == 1
    print(f"W15 self-tests passed (DSU avg hops={avg_hops:.3f}, 1024-inc bit flips={flips}).")


if __name__ == "__main__":
    run_tests()
