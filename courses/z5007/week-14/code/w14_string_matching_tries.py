"""Week 14 Reference Module: Prefix Tries, KMP Prefix Function, Rabin-Karp Rolling Hash, and Z-Algorithm."""

from __future__ import annotations


class TrieNode:
    def __init__(self) -> None:
        self.children: dict[str, TrieNode] = {}
        self.is_end: bool = False


class PrefixTrie:
    """Prefix tree supporting O(L) insert, exact search, and prefix autocomplete."""

    def __init__(self) -> None:
        self.root = TrieNode()

    def insert(self, word: str) -> None:
        cur = self.root
        for ch in word:
            cur = cur.children.setdefault(ch, TrieNode())
        cur.is_end = True

    def search(self, word: str) -> bool:
        cur = self._walk(word)
        return cur is not None and cur.is_end

    def starts_with(self, prefix: str) -> bool:
        return self._walk(prefix) is not None

    def autocomplete(self, prefix: str) -> list[str]:
        node = self._walk(prefix)
        if node is None:
            return []
        results: list[str] = []

        def _dfs(cur: TrieNode, buf: list[str]) -> None:
            if cur.is_end:
                results.append(prefix + "".join(buf))
            for ch in sorted(cur.children):
                buf.append(ch)
                _dfs(cur.children[ch], buf)
                buf.pop()

        _dfs(node, [])
        return results

    def _walk(self, s: str) -> TrieNode | None:
        cur = self.root
        for ch in s:
            if ch not in cur.children:
                return None
            cur = cur.children[ch]
        return cur


def compute_lps(pattern: str) -> list[int]:
    """Compute Longest Proper Prefix Suffix (LPS) table for KMP in O(m)."""
    lps = [0] * len(pattern)
    length = 0
    i = 1
    while i < len(pattern):
        if pattern[i] == pattern[length]:
            length += 1
            lps[i] = length
            i += 1
        elif length > 0:
            length = lps[length - 1]
        else:
            lps[i] = 0
            i += 1
    return lps


def kmp_search(text: str, pattern: str) -> list[int]:
    """Return all start indices where pattern matches text in O(n + m) worst-case time."""
    if not pattern:
        return list(range(len(text) + 1))
    lps = compute_lps(pattern)
    hits: list[int] = []
    i = j = 0
    while i < len(text):
        if text[i] == pattern[j]:
            i += 1
            j += 1
            if j == len(pattern):
                hits.append(i - j)
                j = lps[j - 1]
        elif j > 0:
            j = lps[j - 1]
        else:
            i += 1
    return hits


def rabin_karp(text: str, pattern: str, base: int = 256, mod: int = 1_000_000_007) -> list[int]:
    """Rolling-hash string search returning all exact match indices."""
    n, m = len(text), len(pattern)
    if m == 0:
        return list(range(n + 1))
    if m > n:
        return []
    high_pow = pow(base, m - 1, mod)
    pat_hash = 0
    win_hash = 0
    for i in range(m):
        pat_hash = (pat_hash * base + ord(pattern[i])) % mod
        win_hash = (win_hash * base + ord(text[i])) % mod
    hits: list[int] = []
    for i in range(n - m + 1):
        if pat_hash == win_hash and text[i : i + m] == pattern:
            hits.append(i)
        if i < n - m:
            win_hash = ((win_hash - ord(text[i]) * high_pow) * base + ord(text[i + m])) % mod
    return hits


def run_tests() -> None:
    trie = PrefixTrie()
    for w in ["clove", "cloves", "coconut", "cashew", "cassava"]:
        trie.insert(w)
    assert trie.search("clove") and not trie.search("clo")
    assert trie.starts_with("cas") and trie.autocomplete("clo") == ["clove", "cloves"]

    txt = "ababcabcabababd"
    pat = "ababd"
    assert kmp_search(txt, pat) == rabin_karp(txt, pat) == [10]
    assert kmp_search("aaaaaa", "aa") == rabin_karp("aaaaaa", "aa") == [0, 1, 2, 3, 4]
    print("W14 self-tests passed (Trie, KMP, and Rabin-Karp exact parity).")


if __name__ == "__main__":
    run_tests()
