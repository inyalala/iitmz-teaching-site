"""Z5008 Lab Module 03: Event-Time Tumbling Windows, Watermarks, and Late-Event Handling."""

from __future__ import annotations

from collections import defaultdict


def process_event_stream(
    events: list[tuple[int, str, float]],
    window_size: int = 10,
    watermark_delay: int = 5,
) -> tuple[dict[tuple[int, str], float], list[tuple[int, str, float]]]:
    """Process (event_time_sec, key, amount) events using watermark = max_event_time - delay."""
    max_event_time = 0
    window_sums: dict[tuple[int, str], float] = defaultdict(float)
    dropped_late: list[tuple[int, str, float]] = []

    for ev_time, key, amount in events:
        max_event_time = max(max_event_time, ev_time)
        watermark = max_event_time - watermark_delay
        win_start = (ev_time // window_size) * window_size
        win_end = win_start + window_size
        if win_end <= watermark:
            dropped_late.append((ev_time, key, amount))
        else:
            window_sums[(win_start, key)] += amount
    return dict(window_sums), dropped_late


def run_tests() -> None:
    stream = [
        (2, "M-Pesa", 40.0),
        (8, "M-Pesa", 60.0),
        (12, "TigoPesa", 25.0),
        (19, "M-Pesa", 50.0),   # advances watermark to 19 - 5 = 14 -> [0,10) closed!
        (4, "M-Pesa", 99.0),    # late arrival for closed [0,10) -> dropped
        (16, "TigoPesa", 15.0), # arrives in [10,20) which is still open -> accepted
    ]
    sums, dropped = process_event_stream(stream, window_size=10, watermark_delay=5)
    assert sums[(0, "M-Pesa")] == 100.0
    assert sums[(10, "TigoPesa")] == 40.0
    assert dropped == [(4, "M-Pesa", 99.0)]
    print("BD03 self-tests passed (Event-time watermark windowing and late-event drop verified).")


if __name__ == "__main__":
    run_tests()
