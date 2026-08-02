from __future__ import annotations

import re
from typing import Any, Callable, Iterable

from .store import MemoryBankStore


def evaluate_search(
    store: MemoryBankStore,
    cases: Iterable[dict[str, Any]],
    search: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    search_function = search or store.search
    ranked_cases = 0
    hit_at_1 = 0
    hit_at_3 = 0
    reciprocal_rank = 0.0
    no_result_cases = 0
    no_result_correct = 0
    details: list[dict[str, Any]] = []
    for case in cases:
        result = search_function(
            case["query"],
            limit=10,
            max_chars=100_000,
            **case.get("filters", {}),
        )
        paths = [item["path"] for item in result["results"]]
        expected = set(case.get("expected", []))
        if not expected:
            no_result_cases += 1
            no_result_correct += int(not paths)
            details.append(
                {
                    "query": case["query"],
                    "expected": [],
                    "actual": paths[:3],
                    "reciprocal_rank": None,
                }
            )
            continue
        ranked_cases += 1
        hit_at_1 += int(bool(paths and paths[0] in expected))
        hit_at_3 += int(any(path in expected for path in paths[:3]))
        rank = next(
            (index for index, path in enumerate(paths, start=1) if path in expected),
            None,
        )
        reciprocal = 1.0 / rank if rank else 0.0
        reciprocal_rank += reciprocal
        details.append(
            {
                "query": case["query"],
                "expected": sorted(expected),
                "actual": paths[:3],
                "reciprocal_rank": reciprocal,
            }
        )
    denominator = max(1, ranked_cases)
    return {
        "queries": ranked_cases + no_result_cases,
        "ranked_queries": ranked_cases,
        "hit_at_1": hit_at_1 / denominator,
        "hit_at_3": hit_at_3 / denominator,
        "mrr": reciprocal_rank / denominator,
        "no_result_accuracy": (
            no_result_correct / no_result_cases if no_result_cases else None
        ),
        "details": details,
    }


def legacy_search(store: MemoryBankStore, query: str, **filters: Any) -> dict[str, Any]:
    limit = max(1, min(int(filters.pop("limit", 20)), 100))
    filters.pop("max_chars", None)
    needle = query.casefold()
    terms = [term for term in re.split(r"\s+", needle) if term]
    results: list[dict[str, Any]] = []
    for document in store.documents():
        if not store._matches(document, filters):
            continue
        haystack = document.text.casefold()
        score = sum(haystack.count(term) for term in terms)
        if needle in haystack:
            score += 10
        if score:
            results.append({"path": document.path, "score": score})
    results.sort(key=lambda item: (-item["score"], item["path"].casefold()))
    return {"results": results[:limit]}
