"""Z5008 Lab Module 05: Pipeline Telemetry, Latency Percentiles, and Prometheus Text Exposition."""

from __future__ import annotations

import math
import random


def percentile(values: list[float], p: float) -> float:
    """Compute linear-interpolated p-th percentile (0 <= p <= 100)."""
    if not values:
        raise ValueError("values must be non-empty")
    s = sorted(values)
    k = (len(s) - 1) * (p / 100.0)
    f, c = math.floor(k), math.ceil(k)
    if f == c:
        return s[int(k)]
    return s[f] + (k - f) * (s[c] - s[f])


def format_prometheus_metrics(job_name: str, processed: int, failed: int, latencies_ms: list[float]) -> str:
    """Render Prometheus text exposition lines for batch/streaming observability."""
    p50 = percentile(latencies_ms, 50)
    p95 = percentile(latencies_ms, 95)
    p99 = percentile(latencies_ms, 99)
    lines = [
        "# HELP pipeline_records_total Total records processed by status",
        "# TYPE pipeline_records_total counter",
        f'pipeline_records_total{{job="{job_name}",status="ok"}} {processed}',
        f'pipeline_records_total{{job="{job_name}",status="error"}} {failed}',
        "# HELP pipeline_stage_latency_ms Stage latency summary in milliseconds",
        "# TYPE pipeline_stage_latency_ms gauge",
        f'pipeline_stage_latency_ms{{job="{job_name}",quantile="0.50"}} {p50:.2f}',
        f'pipeline_stage_latency_ms{{job="{job_name}",quantile="0.95"}} {p95:.2f}',
        f'pipeline_stage_latency_ms{{job="{job_name}",quantile="0.99"}} {p99:.2f}',
    ]
    return "\n".join(lines)


def run_tests() -> None:
    rng = random.Random(5008)
    lat = [rng.lognormvariate(3.0, 0.4) for _ in range(500)]
    p50, p95, p99 = percentile(lat, 50), percentile(lat, 95), percentile(lat, 99)
    assert p50 < p95 < p99
    prom = format_prometheus_metrics("zanzibar_lakehouse_etl", 10000, 12, lat)
    assert 'quantile="0.95"' in prom and 'status="ok"} 10000' in prom
    print(f"BD05 self-tests passed (p50={p50:.1f} ms, p95={p95:.1f} ms, p99={p99:.1f} ms).")


if __name__ == "__main__":
    run_tests()
