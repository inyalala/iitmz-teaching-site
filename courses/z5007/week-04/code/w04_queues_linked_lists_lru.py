"""Week 04 Reference Module: Circular Queues, Singly & Doubly Linked Lists, and O(1) LRU Cache."""

from __future__ import annotations

from typing import Any, Optional


class CircularArrayQueue:
    """FIFO queue using modular wrap-around indexing and amortized doubling."""

    def __init__(self, capacity: int = 8) -> None:
        self._data: list[Any] = [None] * capacity
        self._front = 0
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def is_empty(self) -> bool:
        return self._size == 0

    def _resize(self, new_cap: int) -> None:
        block: list[Any] = [None] * new_cap
        cap = len(self._data)
        for k in range(self._size):
            block[k] = self._data[(self._front + k) % cap]
        self._data = block
        self._front = 0

    def enqueue(self, item: Any) -> None:
        if self._size == len(self._data):
            self._resize(2 * len(self._data))
        avail = (self._front + self._size) % len(self._data)
        self._data[avail] = item
        self._size += 1

    def dequeue(self) -> Any:
        if self._size == 0:
            raise IndexError("dequeue from empty queue")
        val = self._data[self._front]
        self._data[self._front] = None
        self._front = (self._front + 1) % len(self._data)
        self._size -= 1
        return val

    def first(self) -> Any:
        if self._size == 0:
            raise IndexError("empty queue")
        return self._data[self._front]


class SNode:
    __slots__ = ("data", "next")

    def __init__(self, data: Any, nxt: Optional[SNode] = None) -> None:
        self.data = data
        self.next = nxt


class SinglyLinkedList:
    """Singly linked list with in-place reversal and Floyd cycle detection."""

    def __init__(self) -> None:
        self.head: Optional[SNode] = None
        self.tail: Optional[SNode] = None
        self._size = 0

    def __len__(self) -> int:
        return self._size

    def append(self, val: Any) -> None:
        node = SNode(val)
        if self.tail is None:
            self.head = self.tail = node
        else:
            self.tail.next = node
            self.tail = node
        self._size += 1

    def to_list(self) -> list[Any]:
        out: list[Any] = []
        cur = self.head
        while cur is not None:
            out.append(cur.data)
            cur = cur.next
        return out

    def reverse_in_place(self) -> None:
        prev: Optional[SNode] = None
        cur = self.head
        self.tail = self.head
        while cur is not None:
            nxt = cur.next
            cur.next = prev
            prev = cur
            cur = nxt
        self.head = prev

    @staticmethod
    def has_cycle(head: Optional[SNode]) -> bool:
        slow = fast = head
        while fast is not None and fast.next is not None:
            slow = slow.next  # type: ignore[assignment]
            fast = fast.next.next
            if slow is fast:
                return True
        return False


class _DNode:
    __slots__ = ("key", "val", "prev", "next")

    def __init__(self, key: Any = None, val: Any = None) -> None:
        self.key = key
        self.val = val
        self.prev: Optional[_DNode] = None
        self.next: Optional[_DNode] = None


class LRUCache:
    """O(1) Least Recently Used cache combining a dict with a sentinel doubly linked list."""

    def __init__(self, capacity: int) -> None:
        if capacity <= 0:
            raise ValueError("capacity must be positive")
        self._cap = capacity
        self._map: dict[Any, _DNode] = {}
        self._head = _DNode()
        self._tail = _DNode()
        self._head.next = self._tail
        self._tail.prev = self._head

    def _remove(self, node: _DNode) -> None:
        assert node.prev is not None and node.next is not None
        node.prev.next = node.next
        node.next.prev = node.prev

    def _insert_front(self, node: _DNode) -> None:
        first = self._head.next
        assert first is not None
        node.prev = self._head
        node.next = first
        self._head.next = node
        first.prev = node

    def get(self, key: Any) -> Any:
        node = self._map.get(key)
        if node is None:
            return None
        self._remove(node)
        self._insert_front(node)
        return node.val

    def put(self, key: Any, val: Any) -> None:
        if key in self._map:
            node = self._map[key]
            node.val = val
            self._remove(node)
            self._insert_front(node)
            return
        if len(self._map) == self._cap:
            lru = self._tail.prev
            assert lru is not None and lru is not self._head
            self._remove(lru)
            del self._map[lru.key]
        node = _DNode(key, val)
        self._map[key] = node
        self._insert_front(node)


def run_tests() -> None:
    q = CircularArrayQueue(3)
    for x in (1, 2, 3, 4, 5):
        q.enqueue(x)
    assert q.dequeue() == 1 and q.dequeue() == 2
    q.enqueue(6)
    assert [q.dequeue() for _ in range(4)] == [3, 4, 5, 6]

    ll = SinglyLinkedList()
    for x in ("A", "B", "C", "D"):
        ll.append(x)
    ll.reverse_in_place()
    assert ll.to_list() == ["D", "C", "B", "A"]
    assert not SinglyLinkedList.has_cycle(ll.head)
    ll.tail.next = ll.head.next  # type: ignore[union-attr]
    assert SinglyLinkedList.has_cycle(ll.head)

    cache = LRUCache(2)
    cache.put("a", 1)
    cache.put("b", 2)
    assert cache.get("a") == 1
    cache.put("c", 3)  # evicts "b"
    assert cache.get("b") is None and cache.get("c") == 3
    print("W04 self-tests passed.")


if __name__ == "__main__":
    run_tests()
