from __future__ import annotations

import math
import re
import time
from collections import Counter
from dataclasses import dataclass
from typing import Any, Callable, Iterable


CAMEL_BOUNDARY_RE = re.compile(
    r"(?<=[a-zа-яё0-9])(?=[A-ZА-ЯЁ])|(?<=[A-ZА-ЯЁ])(?=[A-ZА-ЯЁ][a-zа-яё])"
)
SURFACE_TOKEN_RE = re.compile(r"[^\W_]+(?:[-_/.][^\W_]+)*", re.UNICODE)
SEPARATOR_RE = re.compile(r"[-_/.]+")
WHITESPACE_RE = re.compile(r"\s+")

FIELD_WEIGHTS = {
    "id": 20.0,
    "title": 12.0,
    "aliases": 10.0,
    "keywords": 10.0,
    "component": 8.0,
    "repository": 8.0,
    "headings": 6.0,
    "summary": 4.0,
    "body": 1.0,
}


def normalize_text(value: str) -> str:
    """Normalize human text without discarding identifier boundaries."""
    expanded = CAMEL_BOUNDARY_RE.sub(" ", str(value))
    expanded = SEPARATOR_RE.sub(" ", expanded)
    return WHITESPACE_RE.sub(" ", expanded.casefold().replace("ё", "е")).strip()


def normalize_identifier(value: str) -> str:
    return re.sub(r"[^\w]+", "", str(value).casefold().replace("ё", "е"), flags=re.UNICODE)


def token_groups(value: str) -> list[tuple[str, ...]]:
    """Return one alternative-token group for every surface query token."""
    groups: list[tuple[str, ...]] = []
    for match in SURFACE_TOKEN_RE.finditer(str(value)):
        surface = match.group(0)
        camel_parts = CAMEL_BOUNDARY_RE.sub(" ", surface).split()
        separated_parts = [
            part
            for camel_part in camel_parts
            for part in SEPARATOR_RE.split(camel_part)
            if part
        ]
        variants: list[str] = []
        folded = surface.casefold().replace("ё", "е")
        canonical = SEPARATOR_RE.sub("-", folded).strip("-")
        collapsed = SEPARATOR_RE.sub("", folded)
        for candidate in (folded, canonical, collapsed, *separated_parts):
            normalized = candidate.casefold().replace("ё", "е")
            if normalized and normalized not in variants:
                variants.append(normalized)
        if variants:
            groups.append(tuple(variants))
    return groups


def tokenize(value: str) -> list[str]:
    return [term for group in token_groups(value) for term in group]


def _as_text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, (list, tuple, set)):
        return "\n".join(str(item) for item in value)
    return str(value)


@dataclass
class IndexedDocument:
    source: Any
    fields: dict[str, str]
    normalized_fields: dict[str, str]
    term_frequencies: dict[str, Counter[str]]
    field_lengths: dict[str, int]
    body_sequence: tuple[str, ...]


class SearchIndex:
    """Compact, automatically refreshed in-memory BM25 field index."""

    def __init__(self) -> None:
        self.signatures: dict[str, tuple[int, int]] = {}
        self.documents: dict[str, IndexedDocument] = {}
        self.document_frequency: Counter[str] = Counter()
        self.average_lengths: dict[str, float] = {}
        self.last_build_ms = 0.0

    def refresh(
        self,
        signatures: dict[str, tuple[int, int]],
        changed_documents: dict[str, Any],
    ) -> bool:
        if signatures == self.signatures:
            return False
        started = time.perf_counter()
        removed = set(self.documents) - set(signatures)
        for path in removed:
            self.documents.pop(path, None)
        for path, document in changed_documents.items():
            self.documents[path] = self._index_document(document)
        self.signatures = dict(signatures)
        self._recalculate_corpus()
        self.last_build_ms = (time.perf_counter() - started) * 1000
        return True

    @staticmethod
    def _index_document(document: Any) -> IndexedDocument:
        metadata = document.metadata
        fields = {
            "id": _as_text(metadata.get("id")),
            "title": document.title,
            "aliases": _as_text(metadata.get("aliases")),
            "keywords": _as_text(metadata.get("keywords")),
            "component": _as_text(
                metadata.get("component")
                or metadata.get("components")
                or metadata.get("affected_components")
            ),
            "repository": _as_text(
                metadata.get("repository")
                or metadata.get("affected_repositories")
                or metadata.get("scope")
            ),
            "headings": "\n".join(document.headings),
            "summary": document.summary,
            "body": document.body,
        }
        normalized_fields = {name: normalize_text(text) for name, text in fields.items()}
        term_frequencies = {
            name: Counter(tokenize(text)) for name, text in fields.items()
        }
        field_lengths = {
            name: max(1, sum(frequencies.values()))
            for name, frequencies in term_frequencies.items()
        }
        return IndexedDocument(
            source=document,
            fields=fields,
            normalized_fields=normalized_fields,
            term_frequencies=term_frequencies,
            field_lengths=field_lengths,
            body_sequence=tuple(normalize_text(document.body).split()),
        )

    def _recalculate_corpus(self) -> None:
        self.document_frequency.clear()
        length_totals = Counter()
        for document in self.documents.values():
            seen: set[str] = set()
            for field, frequencies in document.term_frequencies.items():
                length_totals[field] += document.field_lengths[field]
                seen.update(frequencies)
            self.document_frequency.update(seen)
        count = max(1, len(self.documents))
        self.average_lengths = {
            field: max(1.0, length_totals[field] / count) for field in FIELD_WEIGHTS
        }

    def search(
        self,
        query: str,
        *,
        exact: bool = False,
        predicate: Callable[[Any], bool] | None = None,
    ) -> list[dict[str, Any]]:
        groups = token_groups(query)
        if not groups:
            return []
        query_terms = tuple(dict.fromkeys(term for group in groups for term in group))
        phrase = normalize_text(query)
        results: list[dict[str, Any]] = []
        for indexed in self.documents.values():
            if predicate and not predicate(indexed.source):
                continue
            if exact:
                occurrences = sum(
                    text.count(phrase)
                    for text in indexed.normalized_fields.values()
                    if phrase
                )
                if not occurrences:
                    continue
                details = {"exact_phrase": float(occurrences)}
                matched_fields = [
                    field
                    for field, text in indexed.normalized_fields.items()
                    if phrase in text
                ]
                score = float(occurrences)
            else:
                score, details, matched_fields = self._score(
                    indexed, query, groups, query_terms, phrase
                )
                if score <= 0:
                    continue
            results.append(
                {
                    "path": indexed.source.path,
                    "title": indexed.source.title,
                    "metadata": indexed.source.metadata,
                    "fragment": self._best_fragment(indexed, groups, phrase),
                    "score": round(score, 6),
                    "matched_fields": matched_fields,
                    "score_details": {
                        key: round(value, 6)
                        for key, value in details.items()
                        if value
                    },
                }
            )
        results.sort(key=lambda item: (-item["score"], item["path"].casefold()))
        return results

    def _score(
        self,
        document: IndexedDocument,
        query: str,
        groups: list[tuple[str, ...]],
        query_terms: tuple[str, ...],
        phrase: str,
    ) -> tuple[float, dict[str, float], list[str]]:
        details: dict[str, float] = {}
        matched_fields: list[str] = []
        count = max(1, len(self.documents))
        for field, weight in FIELD_WEIGHTS.items():
            frequencies = document.term_frequencies[field]
            length = document.field_lengths[field]
            average = self.average_lengths.get(field, 1.0)
            contribution = 0.0
            for term in query_terms:
                frequency = frequencies.get(term, 0)
                if not frequency:
                    continue
                document_frequency = self.document_frequency.get(term, 0)
                inverse_frequency = math.log(
                    1.0 + (count - document_frequency + 0.5) / (document_frequency + 0.5)
                )
                k1 = 1.2
                b = 0.35 if field in {"id", "title", "aliases", "keywords"} else 0.75
                saturation = (
                    frequency * (k1 + 1.0)
                    / (frequency + k1 * (1.0 - b + b * length / average))
                )
                contribution += inverse_frequency * saturation * weight
            if contribution:
                details[field] = contribution
                matched_fields.append(field)

        identifier = _as_text(document.source.metadata.get("id"))
        if identifier and normalize_identifier(query) == normalize_identifier(identifier):
            details["exact_id"] = 100.0
        normalized_values = tuple(document.normalized_fields.values())
        if phrase and any(phrase in value for value in normalized_values):
            details["exact_phrase"] = 8.0
        if all(
            any(
                variant in frequencies
                for frequencies in document.term_frequencies.values()
                for variant in group
            )
            for group in groups
        ):
            details["all_terms"] = 5.0
        proximity = self._proximity_bonus(document.body_sequence, groups)
        if proximity:
            details["proximity"] = proximity
        return sum(details.values()), details, matched_fields

    @staticmethod
    def _proximity_bonus(
        sequence: tuple[str, ...], groups: list[tuple[str, ...]]
    ) -> float:
        if len(groups) < 2 or not sequence:
            return 0.0
        positions: list[list[int]] = []
        for group in groups:
            alternatives = set(group)
            found = [index for index, term in enumerate(sequence) if term in alternatives]
            if not found:
                return 0.0
            positions.append(found)
        best_span: int | None = None
        for start in positions[0]:
            selected = [start]
            cursor = start
            possible = True
            for candidates in positions[1:]:
                following = next((value for value in candidates if value >= cursor), None)
                if following is None:
                    possible = False
                    break
                selected.append(following)
                cursor = following
            if possible:
                span = selected[-1] - selected[0] + 1
                best_span = span if best_span is None else min(best_span, span)
        if best_span is None:
            return 0.0
        return 4.0 / (1.0 + max(0, best_span - len(groups)))

    @staticmethod
    def _best_fragment(
        document: IndexedDocument,
        groups: list[tuple[str, ...]],
        phrase: str,
        maximum: int = 520,
    ) -> str:
        candidates = [
            WHITESPACE_RE.sub(" ", block).strip()
            for block in re.split(r"\n\s*\n", document.source.body)
            if block.strip()
        ]
        if not candidates:
            return ""

        def quality(candidate: str) -> tuple[int, int, int]:
            normalized = normalize_text(candidate)
            candidate_terms = Counter(tokenize(candidate))
            matched = sum(
                1
                for group in groups
                if any(term in candidate_terms for term in group)
            )
            occurrences = sum(
                candidate_terms.get(term, 0)
                for group in groups
                for term in group
            )
            exact_phrase = int(bool(phrase and phrase in normalized))
            return exact_phrase, matched, occurrences

        best = max(enumerate(candidates), key=lambda item: (quality(item[1]), -item[0]))[1]
        if len(best) <= maximum:
            return best
        normalized = normalize_text(best)
        position = normalized.find(phrase) if phrase else -1
        if position < 0:
            position = min(
                (
                    normalized.find(term)
                    for group in groups
                    for term in group
                    if term in normalized
                ),
                default=0,
            )
        start = max(0, min(len(best) - maximum, position - maximum // 3))
        fragment = best[start : start + maximum].strip()
        return ("… " if start else "") + fragment + (
            " …" if start + maximum < len(best) else ""
        )

    def memory_bytes_estimate(self) -> int:
        """Stable lower-bound estimate useful for comparative benchmark output."""
        return sum(
            sum(len(value.encode("utf-8")) for value in document.fields.values())
            + sum(
                len(term.encode("utf-8")) + 16
                for frequencies in document.term_frequencies.values()
                for term in frequencies
            )
            for document in self.documents.values()
        )
