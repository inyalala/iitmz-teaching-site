"""Week 06 Reference Module: Binary Trees, Four Traversals, BST Operations, and Rebuild."""

from __future__ import annotations

from collections import deque
import random
from typing import Any, Optional


class TreeNode:
    """Binary tree node storing a key and optional left/right children."""

    def __init__(self, key: Any, left: Optional[TreeNode] = None, right: Optional[TreeNode] = None) -> None:
        self.key = key
        self.left = left
        self.right = right


def preorder(root: Optional[TreeNode]) -> list[Any]:
    return [] if root is None else [root.key] + preorder(root.left) + preorder(root.right)


def inorder(root: Optional[TreeNode]) -> list[Any]:
    return [] if root is None else inorder(root.left) + [root.key] + inorder(root.right)


def postorder(root: Optional[TreeNode]) -> list[Any]:
    return [] if root is None else postorder(root.left) + postorder(root.right) + [root.key]


def level_order(root: Optional[TreeNode]) -> list[Any]:
    if root is None:
        return []
    out: list[Any] = []
    q: deque[TreeNode] = deque([root])
    while q:
        cur = q.popleft()
        out.append(cur.key)
        if cur.left is not None:
            q.append(cur.left)
        if cur.right is not None:
            q.append(cur.right)
    return out


def height(root: Optional[TreeNode]) -> int:
    if root is None:
        return -1
    return 1 + max(height(root.left), height(root.right))


def count_nodes(root: Optional[TreeNode]) -> int:
    if root is None:
        return 0
    return 1 + count_nodes(root.left) + count_nodes(root.right)


def bst_insert(root: Optional[TreeNode], key: Any) -> TreeNode:
    if root is None:
        return TreeNode(key)
    if key < root.key:
        root.left = bst_insert(root.left, key)
    else:
        root.right = bst_insert(root.right, key)
    return root


def bst_search(root: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
    cur = root
    while cur is not None:
        if key == cur.key:
            return cur
        cur = cur.left if key < cur.key else cur.right
    return None


def bst_min(root: TreeNode) -> Any:
    cur = root
    while cur.left is not None:
        cur = cur.left
    return cur.key


def bst_delete(root: Optional[TreeNode], key: Any) -> Optional[TreeNode]:
    """Delete one occurrence of key using inorder successor replacement."""
    if root is None:
        return None
    if key < root.key:
        root.left = bst_delete(root.left, key)
    elif key > root.key:
        root.right = bst_delete(root.right, key)
    else:
        if root.left is None:
            return root.right
        if root.right is None:
            return root.left
        succ_key = bst_min(root.right)
        root.key = succ_key
        root.right = bst_delete(root.right, succ_key)
    return root


def bst_range_query(root: Optional[TreeNode], lo: Any, hi: Any) -> list[Any]:
    """Return sorted keys within [lo, hi] while pruning impossible subtrees."""
    out: list[Any] = []

    def _dfs(node: Optional[TreeNode]) -> None:
        if node is None:
            return
        if lo < node.key:
            _dfs(node.left)
        if lo <= node.key <= hi:
            out.append(node.key)
        if node.key < hi:
            _dfs(node.right)

    _dfs(root)
    return out


def is_bst(root: Optional[TreeNode], lo: Any = None, hi: Any = None) -> bool:
    if root is None:
        return True
    if lo is not None and root.key < lo:
        return False
    if hi is not None and root.key >= hi:
        return False
    return is_bst(root.left, lo, root.key) and is_bst(root.right, root.key, hi)


def rebuild_from_pre_in(pre: list[Any], ino: list[Any]) -> Optional[TreeNode]:
    if not pre:
        return None
    root_val = pre[0]
    k = ino.index(root_val)
    return TreeNode(
        root_val,
        rebuild_from_pre_in(pre[1 : 1 + k], ino[:k]),
        rebuild_from_pre_in(pre[1 + k :], ino[k + 1 :]),
    )


def run_tests() -> None:
    keys = [8, 3, 10, 1, 6, 14, 4, 7, 13]
    root: Optional[TreeNode] = None
    for k in keys:
        root = bst_insert(root, k)
    assert inorder(root) == sorted(keys)
    assert preorder(root) == [8, 3, 1, 6, 4, 7, 10, 14, 13]
    assert level_order(root) == [8, 3, 10, 1, 6, 14, 4, 7, 13]
    assert bst_range_query(root, 4, 10) == [4, 6, 7, 8, 10]
    assert is_bst(root)

    bad = TreeNode(10, TreeNode(5, TreeNode(2), TreeNode(12)), TreeNode(15))
    assert not is_bst(bad)

    root = bst_delete(root, 3)
    assert inorder(root) == [1, 4, 6, 7, 8, 10, 13, 14] and is_bst(root)

    rebuilt = rebuild_from_pre_in(preorder(root), inorder(root))
    assert preorder(rebuilt) == preorder(root) and inorder(rebuilt) == inorder(root)

    rng = random.Random(6)
    rkeys = rng.sample(range(500), 127)
    rtree: Optional[TreeNode] = None
    for k in rkeys:
        rtree = bst_insert(rtree, k)
    assert height(rtree) < 25
    print(f"W06 self-tests passed (random 127-node BST height = {height(rtree)}).")


if __name__ == "__main__":
    run_tests()
