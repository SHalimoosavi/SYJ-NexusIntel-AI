"""Small per-process abuse limiter.

For multi-worker/replica production deployments, configure an upstream shared
Redis-backed gateway limiter as well. This in-process layer is defense-in-depth.
"""
from collections import defaultdict, deque
from threading import Lock
from time import monotonic


class SlidingWindowLimiter:
    def __init__(self):
        self._events: dict[str, deque[float]] = defaultdict(deque)
        self._lock = Lock()

    def allow(self, key: str, limit: int, window_seconds: int) -> bool:
        now = monotonic()
        cutoff = now - window_seconds
        with self._lock:
            events = self._events[key]
            while events and events[0] <= cutoff:
                events.popleft()
            if len(events) >= limit:
                return False
            events.append(now)
            return True


limiter = SlidingWindowLimiter()
