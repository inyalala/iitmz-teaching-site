"""Z3003 Module 04: MapReduce Engine and PySpark RDD/DataFrame Pipeline."""

from __future__ import annotations

from collections import defaultdict
import re
from typing import Callable, Iterable, TypeVar

T = TypeVar("T")
K = TypeVar("K")
V = TypeVar("V")
R = TypeVar("R")


def run_mapreduce(
    records: Iterable[T],
    mapper: Callable[[T], Iterable[tuple[K, V]]],
    reducer: Callable[[K, list[V]], R],
) -> dict[K, R]:
    """Execute deterministic in-memory Map -> Shuffle -> Reduce pipeline."""
    grouped: dict[K, list[V]] = defaultdict(list)
    for rec in records:
        for key, val in mapper(rec):
            grouped[key].append(val)
    return {k: reducer(k, vals) for k, vals in grouped.items()}


LOG_RE = re.compile(r'(\S+) \S+ \S+ \[([^\]]+)\] "(\S+) (\S+) \S+" (\d+) (\S+)')


def parse_http_log_line(line: str) -> tuple[str, str, int, int] | None:
    """Parse (host, path, status, bytes) from an Apache/NASA HTTP log line."""
    m = LOG_RE.match(line)
    if not m:
        return None
    host, _, _, path, status, size_str = m.groups()
    nbytes = 0 if size_str == "-" else int(size_str)
    return host, path, int(status), nbytes


def run_tests() -> None:
    docs = [
        "data mining scales with spark",
        "spark map reduce processes data",
        "map shuffle reduce on large data",
    ]
    wc = run_mapreduce(
        docs,
        mapper=lambda line: ((w, 1) for w in line.split()),
        reducer=lambda k, vals: sum(vals),
    )
    assert wc["data"] == 3 and wc["spark"] == 2 and wc["reduce"] == 2

    sample_logs = [
        '199.72.81.55 - - [01/Jul/1995:00:00:01 -0400] "GET /history/apollo/ HTTP/1.0" 200 6245',
        '199.72.81.55 - - [01/Jul/1995:00:00:02 -0400] "GET /missing.gif HTTP/1.0" 404 -',
        'piweba3y.prodigy.com - - [01/Jul/1995:00:00:05 -0400] "GET /ksc.html HTTP/1.0" 200 7074',
    ]
    parsed = [p for p in (parse_http_log_line(ln) for ln in sample_logs) if p is not None]
    status_counts = run_mapreduce(
        parsed,
        mapper=lambda rec: [(rec[2], 1)],
        reducer=lambda k, vals: sum(vals),
    )
    assert status_counts == {200: 2, 404: 1}
    host_bytes = run_mapreduce(
        parsed,
        mapper=lambda rec: [(rec[0], rec[3])],
        reducer=lambda k, vals: sum(vals),
    )
    assert host_bytes["199.72.81.55"] == 6245

    # Algebraic vs distributive OLAP aggregation via MapReduce: (sum, count) -> mean
    farm_rows = [("Pemba", 2.0), ("Pemba", 3.0), ("Unguja", 1.5), ("Unguja", 2.5), ("Unguja", 2.0)]
    sums_cnts = run_mapreduce(
        farm_rows,
        mapper=lambda r: [(r[0], (r[1], 1))],
        reducer=lambda k, vs: (sum(x for x, _ in vs), sum(c for _, c in vs)),
    )
    avgs = {k: s / c for k, (s, c) in sums_cnts.items()}
    assert abs(avgs["Pemba"] - 2.5) < 1e-9 and abs(avgs["Unguja"] - 2.0) < 1e-9
    print("DM04 self-tests passed (MapReduce word count, HTTP log parse, distributive OLAP AVG).")


if __name__ == "__main__":
    run_tests()
