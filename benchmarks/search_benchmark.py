from __future__ import annotations

import json
import statistics
import tempfile
import time
import tracemalloc
from pathlib import Path

from memory_bank_mcp.store import MemoryBankStore


QUERIES = [
    "SPEC-0042",
    "KafkaAdapter",
    "фоновая обработка",
    "producer_queue retry",
    "consumer/group offset",
]


def document(index: int, extra: str = "") -> str:
    return f"""---
title: Component {index}
id: SPEC-{index:04d}
type: specification
status: verified
updated: 2026-07-30
aliases:
  - Компонент {index}
keywords:
  - KafkaAdapter
  - producer_queue
repository: kafka-adapter
component: component-{index % 10}
---

# Component {index}

## Summary

Фоновая обработка component {index} manages consumer/group offsets.

## Details

KafkaAdapter retries producer_queue delivery and records diagnostics. {extra}
"""


def percentile(samples: list[float], fraction: float) -> float:
    ordered = sorted(samples)
    return ordered[int((len(ordered) - 1) * fraction)]


def legacy_search(root: Path, query: str) -> None:
    needle = query.casefold()
    terms = needle.split()
    scores = []
    for path in sorted(root.glob("*.md")):
        text = path.read_text(encoding="utf-8").casefold()
        score = sum(text.count(term) for term in terms)
        if needle in text:
            score += 10
        if score:
            scores.append((score, path.name))
    scores.sort(key=lambda item: (-item[0], item[1]))


def timed_calls(callable_, iterations: int = 100) -> list[float]:
    samples: list[float] = []
    for index in range(iterations):
        started = time.perf_counter()
        callable_(QUERIES[index % len(QUERIES)])
        samples.append((time.perf_counter() - started) * 1000)
    return samples


def main() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = Path(directory)
        for index in range(1, 101):
            (root / f"document-{index:03d}.md").write_text(
                document(index), encoding="utf-8"
            )

        legacy_samples = timed_calls(lambda query: legacy_search(root, query))

        store = MemoryBankStore(root)
        tracemalloc.start()
        started = time.perf_counter()
        store.search("SPEC-0042", max_chars=100_000)
        build_ms = (time.perf_counter() - started) * 1000
        _, peak_bytes = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        indexed_samples = timed_calls(
            lambda query: store.search(query, max_chars=100_000)
        )

        target = "document-042.md"
        revision = store.get(target).revision
        started = time.perf_counter()
        store.update(
            target,
            document(42, "single document update marker"),
            expected_revision=revision,
        )
        store.search("single document update marker", max_chars=100_000)
        update_ms = (time.perf_counter() - started) * 1000

        result = {
            "documents": 100,
            "legacy_search_ms": {
                "p50": round(statistics.median(legacy_samples), 3),
                "p95": round(percentile(legacy_samples, 0.95), 3),
            },
            "indexed_search_ms": {
                "build": round(build_ms, 3),
                "p50": round(statistics.median(indexed_samples), 3),
                "p95": round(percentile(indexed_samples, 0.95), 3),
                "single_document_update": round(update_ms, 3),
            },
            "index_memory": {
                "tracemalloc_peak_bytes": peak_bytes,
                "estimated_payload_bytes": store._search_index.memory_bytes_estimate(),
            },
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        if build_ms > 10_000 or percentile(indexed_samples, 0.95) > 1_000:
            raise SystemExit("Search benchmark smoke threshold exceeded")


if __name__ == "__main__":
    main()

