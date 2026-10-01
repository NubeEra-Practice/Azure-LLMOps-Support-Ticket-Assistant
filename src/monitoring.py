from __future__ import annotations

from collections import Counter
from threading import Lock
from time import perf_counter


class RequestMetrics:
    def __init__(self) -> None:
        self._lock = Lock()
        self._counts: Counter[str] = Counter()
        self._latency_ms: list[float] = []
        self._prompt_tokens = 0
        self._completion_tokens = 0
        self._estimated_cost_usd: float | None = 0.0

    def observe(
        self,
        route: str,
        elapsed_ms: float,
        outcome: str = "ok",
        usage: dict[str, int | float | None] | None = None,
    ) -> None:
        with self._lock:
            self._counts[f"{route}:{outcome}"] += 1
            self._latency_ms.append(elapsed_ms)
            if usage:
                self._prompt_tokens += int(usage.get("prompt_tokens", 0) or 0)
                self._completion_tokens += int(usage.get("completion_tokens", 0) or 0)
                cost = usage.get("estimated_cost_usd")
                if cost is None:
                    self._estimated_cost_usd = None
                elif self._estimated_cost_usd is not None:
                    self._estimated_cost_usd += float(cost)
            if len(self._latency_ms) > 10000:
                self._latency_ms = self._latency_ms[-5000:]

    def snapshot(self) -> dict[str, int | float | None]:
        with self._lock:
            latencies = list(self._latency_ms)
            result: dict[str, int | float | None] = {k: v for k, v in self._counts.items()}
            result["prompt_tokens_total"] = self._prompt_tokens
            result["completion_tokens_total"] = self._completion_tokens
            result["estimated_cost_usd_total"] = self._estimated_cost_usd
            result["requests_total"] = sum(self._counts.values())
        result["latency_ms_avg"] = round(sum(latencies) / len(latencies), 2) if latencies else 0.0
        result["latency_ms_max"] = round(max(latencies), 2) if latencies else 0.0
        return result


def elapsed_ms(start: float) -> float:
    return (perf_counter() - start) * 1000
