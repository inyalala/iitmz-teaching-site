"""Week 12 Reference Module: Dynamic Programming (Memoization, Tabulation, 0/1 Knapsack, LCS, Edit Distance)."""

from __future__ import annotations

from functools import lru_cache


def fib_memo(n: int) -> int:
    """Top-down memoized Fibonacci in O(n) time."""
    memo: dict[int, int] = {0: 0, 1: 1}

    def _f(k: int) -> int:
        if k not in memo:
            memo[k] = _f(k - 1) + _f(k - 2)
        return memo[k]

    return _f(n)


def fib_tab(n: int) -> int:
    """Bottom-up O(1)-space Fibonacci."""
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def coin_change_min(coins: list[int], amount: int) -> int:
    """Minimum coins to sum to amount, or -1 if impossible."""
    inf = amount + 1
    dp = [inf] * (amount + 1)
    dp[0] = 0
    for x in range(1, amount + 1):
        for c in coins:
            if c <= x and dp[x - c] + 1 < dp[x]:
                dp[x] = dp[x - c] + 1
    return -1 if dp[amount] == inf else dp[amount]


def knapsack_01(capacity: int, items: list[tuple[int, int]]) -> tuple[int, list[int]]:
    """0/1 Knapsack returning (max_value, chosen_indices) for (value, weight) pairs."""
    n = len(items)
    dp = [[0] * (capacity + 1) for _ in range(n + 1)]
    for i in range(1, n + 1):
        val, wt = items[i - 1]
        for w in range(capacity + 1):
            dp[i][w] = dp[i - 1][w]
            if wt <= w and dp[i - 1][w - wt] + val > dp[i][w]:
                dp[i][w] = dp[i - 1][w - wt] + val

    chosen: list[int] = []
    w = capacity
    for i in range(n, 0, -1):
        if dp[i][w] != dp[i - 1][w]:
            chosen.append(i - 1)
            w -= items[i - 1][1]
    chosen.reverse()
    return dp[n][capacity], chosen


def lcs(a: str, b: str) -> tuple[int, str]:
    """Longest Common Subsequence length and reconstructed string."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if a[i - 1] == b[j - 1]:
                dp[i][j] = dp[i - 1][j - 1] + 1
            else:
                dp[i][j] = max(dp[i - 1][j], dp[i][j - 1])

    out: list[str] = []
    i, j = m, n
    while i > 0 and j > 0:
        if a[i - 1] == b[j - 1]:
            out.append(a[i - 1])
            i -= 1
            j -= 1
        elif dp[i - 1][j] >= dp[i][j - 1]:
            i -= 1
        else:
            j -= 1
    out.reverse()
    return dp[m][n], "".join(out)


def edit_distance(a: str, b: str) -> int:
    """Levenshtein edit distance (insert, delete, substitute) in O(mn) time."""
    m, n = len(a), len(b)
    dp = [[0] * (n + 1) for _ in range(m + 1)]
    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j
    for i in range(1, m + 1):
        for j in range(1, n + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + cost)
    return dp[m][n]


def run_tests() -> None:
    assert fib_memo(35) == fib_tab(35) == 9227465
    assert coin_change_min([1, 5, 10, 25], 63) == 6
    assert coin_change_min([2], 3) == -1

    # Notice fractional greedy picks item 0 (60,10) + item 1 (100,20) = 160, whereas 0/1 takes (100,20)+(120,30)=220!
    best_val, chosen = knapsack_01(50, [(60, 10), (100, 20), (120, 30)])
    assert best_val == 220 and chosen == [1, 2]

    length, subseq = lcs("ZANZIBAR", "BANAIR")
    assert length == 4 and subseq == "ANIR"
    assert edit_distance("kitten", "sitting") == 3
    assert edit_distance("clove", "cloves") == 1
    print("W12 self-tests passed.")


if __name__ == "__main__":
    run_tests()
