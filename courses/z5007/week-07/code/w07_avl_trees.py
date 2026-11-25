"""Week 07 Reference Module: Self-Balancing AVL Trees (LL, RR, LR, RL Rotations & Height Bound)."""

from __future__ import annotations

import math
import random
from typing import Any, Optional


class AVLNode:
    """Node of an AVL tree caching subtree height for O(1) balance factor checks."""

    def __init__(self, key: Any) -> None:
        self.key = key
        self.left: Optional[AVLNode] = None
        self.right: Optional[AVLNode] = None
        self.height: int = 0


def _height(node: Optional[AVLNode]) -> int:
    return -1 if node is None else node.height


def _update_height(node: AVLNode) -> None:
    node.height = 1 + max(_height(node.left), _height(node.right))


def balance_factor(node: Optional[AVLNode]) -> int:
    """Return height(left) - height(right)."""
    if node is None:
        return 0
    return _height(node.left) - _height(node.right)


def rotate_right(z: AVLNode) -> AVLNode:
    """LL repair: single right rotation around z."""
    y = z.left
    assert y is not None
    t3 = y.right
    y.right = z
    z.left = t3
    _update_height(z)
    _update_height(y)
    return y


def rotate_left(z: AVLNode) -> AVLNode:
    """RR repair: single left rotation around z."""
    y = z.right
    assert y is not None
    t2 = y.left
    y.left = z
    z.right = t2
    _update_height(z)
    _update_height(y)
    return y


def _rebalance(node: AVLNode) -> AVLNode:
    _update_height(node)
    bf = balance_factor(node)
    if bf > 1:
        if balance_factor(node.left) < 0:  # LR case
            assert node.left is not None
            node.left = rotate_left(node.left)
        return rotate_right(node)  # LL case
    if bf < -1:
        if balance_factor(node.right) > 0:  # RL case
            assert node.right is not None
            node.right = rotate_right(node.right)
        return rotate_left(node)  # RR case
    return node


def avl_insert(node: Optional[AVLNode], key: Any) -> AVLNode:
    """Insert key into AVL tree and restore balance along the return path."""
    if node is None:
        return AVLNode(key)
    if key < node.key:
        node.left = avl_insert(node.left, key)
    elif key > node.key:
        node.right = avl_insert(node.right, key)
    else:
        return node
    return _rebalance(node)


def _min_node(node: AVLNode) -> AVLNode:
    cur = node
    while cur.left is not None:
        cur = cur.left
    return cur


def avl_delete(node: Optional[AVLNode], key: Any) -> Optional[AVLNode]:
    """Delete key from AVL tree and rebalance upward."""
    if node is None:
        return None
    if key < node.key:
        node.left = avl_delete(node.left, key)
    elif key > node.key:
        node.right = avl_delete(node.right, key)
    else:
        if node.left is None:
            return node.right
        if node.right is None:
            return node.left
        succ = _min_node(node.right)
        node.key = succ.key
        node.right = avl_delete(node.right, succ.key)
    return _rebalance(node)


def verify_avl(node: Optional[AVLNode], lo: Any = None, hi: Any = None) -> tuple[bool, int]:
    """Verify BST ordering, cached heights, and |bf| <= 1 at every node."""
    if node is None:
        return True, -1
    if (lo is not None and node.key <= lo) or (hi is not None and node.key >= hi):
        return False, 0
    ok_l, hl = verify_avl(node.left, lo, node.key)
    ok_r, hr = verify_avl(node.right, node.key, hi)
    if not ok_l or not ok_r:
        return False, 0
    if abs(hl - hr) > 1 or node.height != 1 + max(hl, hr):
        return False, 0
    return True, node.height


def avl_inorder(node: Optional[AVLNode]) -> list[Any]:
    return [] if node is None else avl_inorder(node.left) + [node.key] + avl_inorder(node.right)


def fibonacci_min_nodes(h: int) -> int:
    """Minimum nodes N(h) in an AVL tree of height h: N(h) = F_{h+3} - 1."""
    if h < 0:
        return 0
    a, b = 1, 2
    for _ in range(h):
        a, b = b, a + b
    return a


def run_tests() -> None:
    # Classroom worksheet sequence: 60, 30, 40, 80, 70, 90, 75 -> delete 30
    root: Optional[AVLNode] = None
    for k in (60, 30, 40, 80, 70, 90, 75):
        root = avl_insert(root, k)
        ok, _ = verify_avl(root)
        assert ok
    root = avl_delete(root, 30)
    ok, _ = verify_avl(root)
    assert ok and avl_inorder(root) == [40, 60, 70, 75, 80, 90]

    # Adversarial sorted insertion of 1,000 keys
    n = 1000
    sorted_avl: Optional[AVLNode] = None
    for k in range(n):
        sorted_avl = avl_insert(sorted_avl, k)
    ok, h = verify_avl(sorted_avl)
    bound = 1.44 * math.log2(n + 2) - 0.328
    assert ok and h <= bound
    assert n >= fibonacci_min_nodes(h)

    # Randomized insert + delete stress
    rng = random.Random(7)
    vals = list(range(200))
    rng.shuffle(vals)
    t: Optional[AVLNode] = None
    for v in vals:
        t = avl_insert(t, v)
    for v in vals[:100]:
        t = avl_delete(t, v)
        ok, _ = verify_avl(t)
        assert ok
    assert avl_inorder(t) == sorted(vals[100:])
    print(f"W07 self-tests passed (sorted 1000-node AVL height={h}, bound={bound:.2f}).")


if __name__ == "__main__":
    run_tests()
