from __future__ import annotations

from collections import defaultdict, deque
from collections.abc import Iterable
from threading import Lock
from time import monotonic


class InMemoryRateLimiter:
    def __init__(self) -> None:
        self._lock = Lock()
        self._requests: dict[tuple[str, str], deque[float]] = defaultdict(deque)

    def allow(self, *, key: str, bucket: str, limit: int, window_seconds: int) -> bool:
        now = monotonic()
        min_ts = now - window_seconds
        entry_key = (bucket, key)

        with self._lock:
            requests = self._requests[entry_key]
            while requests and requests[0] <= min_ts:
                requests.popleft()

            if len(requests) >= limit:
                return False

            requests.append(now)
            return True

    def clear(self) -> None:
        with self._lock:
            self._requests.clear()


SENSITIVE_POST_PATHS: tuple[str, ...] = (
    "/api/v1/auth/bootstrap-owner",
    "/api/v1/auth/login",
    "/api/v1/auth/refresh",
    "/api/v1/auth/logout",
)


def is_rate_limited_endpoint(path: str, method: str, sensitive_paths: Iterable[str]) -> bool:
    if method.upper() != "POST":
        return False
    return path in sensitive_paths
