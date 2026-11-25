"""Z5008 Lab Module 06: Airflow-Style DAG Orchestration, Idempotent Retries, and SLA Checks."""

from __future__ import annotations

from collections import deque
from dataclasses import dataclass, field
from typing import Callable


@dataclass
class TaskNode:
    """Declarative workflow task mirroring an Apache Airflow operator."""

    task_id: str
    fn: Callable[[dict[str, object]], object]
    retries: int = 1
    sla_seconds: float = 10.0
    upstream: list[str] = field(default_factory=list)


class MiniDagScheduler:
    """Validate acyclicity, execute tasks in topological order, track XComs and SLAs."""

    def __init__(self, dag_id: str) -> None:
        self.dag_id = dag_id
        self.tasks: dict[str, TaskNode] = {}

    def add_task(self, node: TaskNode) -> None:
        self.tasks[node.task_id] = node

    def topological_order(self) -> list[str]:
        indeg = {tid: 0 for tid in self.tasks}
        children: dict[str, list[str]] = {tid: [] for tid in self.tasks}
        for tid, node in self.tasks.items():
            for up in node.upstream:
                if up not in self.tasks:
                    raise ValueError(f"Unknown upstream task: {up}")
                children[up].append(tid)
                indeg[tid] += 1
        q = deque(sorted(tid for tid, d in indeg.items() if d == 0))
        order: list[str] = []
        while q:
            u = q.popleft()
            order.append(u)
            for v in sorted(children[u]):
                indeg[v] -= 1
                if indeg[v] == 0:
                    q.append(v)
        if len(order) != len(self.tasks):
            raise ValueError(f"Cycle detected in DAG {self.dag_id}")
        return order

    def run(self, durations: dict[str, float] | None = None) -> dict[str, object]:
        order = self.topological_order()
        xcoms: dict[str, object] = {}
        attempts: dict[str, int] = {}
        sla_misses: list[str] = []
        elapsed_map = durations or {}

        for tid in order:
            node = self.tasks[tid]
            last_err: Exception | None = None
            for attempt in range(1, node.retries + 2):
                attempts[tid] = attempt
                try:
                    xcoms[tid] = node.fn(xcoms)
                    last_err = None
                    break
                except Exception as exc:  # noqa: BLE001
                    last_err = exc
            if last_err is not None:
                raise RuntimeError(f"Task {tid} failed after {attempts[tid]} attempts") from last_err
            if elapsed_map.get(tid, 0.0) > node.sla_seconds:
                sla_misses.append(tid)
        return {"order": order, "xcoms": xcoms, "attempts": attempts, "sla_misses": sla_misses}


def run_tests() -> None:
    flaky_state = {"calls": 0}

    def extract_bronze(_: dict[str, object]) -> str:
        return "s3://lakehouse/bronze/2026-11-26/"

    def transform_silver(xcom: dict[str, object]) -> dict[str, object]:
        flaky_state["calls"] += 1
        if flaky_state["calls"] == 1:
            raise TimeoutError("Transient object-store timeout")
        # Idempotent deterministic output URI keyed by partition date
        return {"uri": str(xcom["extract_bronze"]).replace("bronze", "silver"), "rows": 12500}

    def load_gold(xcom: dict[str, object]) -> str:
        meta = xcom["transform_silver"]
        assert isinstance(meta, dict)
        return f"gold_ready:{meta['rows']}"

    dag = MiniDagScheduler("zanzibar_daily_lakehouse")
    dag.add_task(TaskNode("extract_bronze", extract_bronze, retries=0, sla_seconds=5.0))
    dag.add_task(
        TaskNode("transform_silver", transform_silver, retries=2, sla_seconds=8.0, upstream=["extract_bronze"])
    )
    dag.add_task(TaskNode("load_gold", load_gold, retries=1, sla_seconds=4.0, upstream=["transform_silver"]))

    report = dag.run(durations={"extract_bronze": 2.1, "transform_silver": 9.4, "load_gold": 1.8})
    assert report["order"] == ["extract_bronze", "transform_silver", "load_gold"]
    assert report["attempts"]["transform_silver"] == 2
    assert report["xcoms"]["load_gold"] == "gold_ready:12500"
    assert report["sla_misses"] == ["transform_silver"]

    # Cycle detection check
    cyclic = MiniDagScheduler("bad_cycle")
    cyclic.add_task(TaskNode("A", lambda _: 1, upstream=["B"]))
    cyclic.add_task(TaskNode("B", lambda _: 2, upstream=["A"]))
    try:
        cyclic.topological_order()
        raise AssertionError("Expected cycle error")
    except ValueError:
        pass
    print("BD06 self-tests passed (Topological execution, retry recovery, cycle check, SLA verified).")


if __name__ == "__main__":
    run_tests()
