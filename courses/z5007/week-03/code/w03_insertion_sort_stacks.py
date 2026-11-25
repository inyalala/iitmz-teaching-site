"""Week 03 Reference Module: Insertion Sort, ArrayStack, LinkedStack, Brackets, Postfix, MinStack."""

from __future__ import annotations

from typing import Any, Optional


def insertion_sort(arr: list[Any]) -> tuple[int, int]:
    """In-place stable Insertion Sort returning (comparisons, shifts)."""
    comps = shifts = 0
    for i in range(1, len(arr)):
        key = arr[i]
        j = i - 1
        while j >= 0:
            comps += 1
            if arr[j] > key:
                arr[j + 1] = arr[j]
                shifts += 1
                j -= 1
            else:
                break
        arr[j + 1] = key
    return comps, shifts


class ArrayStack:
    """LIFO stack backed by a doubling contiguous block."""

    def __init__(self, capacity: int = 8) -> None:
        self._data: list[Any] = [None] * capacity
        self._top = -1

    def is_empty(self) -> bool:
        return self._top == -1

    def __len__(self) -> int:
        return self._top + 1

    def _resize(self, cap: int) -> None:
        block: list[Any] = [None] * cap
        for i in range(self._top + 1):
            block[i] = self._data[i]
        self._data = block

    def push(self, item: Any) -> None:
        if self._top + 1 == len(self._data):
            self._resize(2 * len(self._data))
        self._top += 1
        self._data[self._top] = item

    def pop(self) -> Any:
        if self._top == -1:
            raise IndexError("pop from empty stack")
        val = self._data[self._top]
        self._data[self._top] = None
        self._top -= 1
        return val

    def peek(self) -> Any:
        if self._top == -1:
            raise IndexError("peek at empty stack")
        return self._data[self._top]


class _Node:
    __slots__ = ("data", "next")

    def __init__(self, data: Any, nxt: Optional[_Node] = None) -> None:
        self.data = data
        self.next = nxt


class LinkedStack:
    """LIFO stack on a singly linked chain where head is the stack top."""

    def __init__(self) -> None:
        self._head: Optional[_Node] = None
        self._size = 0

    def is_empty(self) -> bool:
        return self._head is None

    def __len__(self) -> int:
        return self._size

    def push(self, item: Any) -> None:
        self._head = _Node(item, self._head)
        self._size += 1

    def pop(self) -> Any:
        if self._head is None:
            raise IndexError("pop from empty stack")
        val = self._head.data
        self._head = self._head.next
        self._size -= 1
        return val

    def peek(self) -> Any:
        if self._head is None:
            raise IndexError("peek at empty stack")
        return self._head.data


class MinStack:
    """Stack supporting O(1) push, pop, peek, and get_min."""

    def __init__(self) -> None:
        self._vals = ArrayStack()
        self._mins = ArrayStack()

    def push(self, x: int) -> None:
        self._vals.push(x)
        if self._mins.is_empty() or x <= self._mins.peek():
            self._mins.push(x)

    def pop(self) -> int:
        val = self._vals.pop()
        if val == self._mins.peek():
            self._mins.pop()
        return val

    def get_min(self) -> int:
        return self._mins.peek()


def is_balanced_brackets(text: str, stack_cls: type = ArrayStack) -> bool:
    """Check whether (), [], and {} brackets are balanced using stack_cls."""
    pairs = {")": "(", "]": "[", "}": "{"}
    openers = set(pairs.values())
    s = stack_cls()
    for ch in text:
        if ch in openers:
            s.push(ch)
        elif ch in pairs:
            if s.is_empty() or s.pop() != pairs[ch]:
                return False
    return s.is_empty()


def eval_postfix(expr: str) -> float:
    """Evaluate a space-separated Reverse Polish Notation expression."""
    s = LinkedStack()
    for tok in expr.split():
        if tok in {"+", "-", "*", "/"}:
            b, a = s.pop(), s.pop()
            if tok == "+":
                s.push(a + b)
            elif tok == "-":
                s.push(a - b)
            elif tok == "*":
                s.push(a * b)
            else:
                s.push(a / b)
        else:
            s.push(float(tok))
    res = s.pop()
    if not s.is_empty():
        raise ValueError("malformed postfix expression")
    return res


def run_tests() -> None:
    arr = [4, 2, 5, 1, 3]
    _, shifts = insertion_sort(arr)
    assert arr == [1, 2, 3, 4, 5] and shifts == 6

    for cls in (ArrayStack, LinkedStack):
        assert is_balanced_brackets("([{}])", cls)
        assert not is_balanced_brackets("([)]", cls)
        assert not is_balanced_brackets("((()", cls)

    ms = MinStack()
    for v in (5, 3, 7, 3, 2):
        ms.push(v)
    assert ms.get_min() == 2
    assert ms.pop() == 2 and ms.get_min() == 3
    assert ms.pop() == 3 and ms.get_min() == 3

    assert abs(eval_postfix("3 4 + 2 * 7 /") - 2.0) < 1e-9
    print("W03 self-tests passed.")


if __name__ == "__main__":
    run_tests()
