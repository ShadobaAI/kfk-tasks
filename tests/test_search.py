from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from memory_bank_mcp.evaluation import evaluate_search, legacy_search
from memory_bank_mcp.search import normalize_identifier, normalize_text, tokenize
from memory_bank_mcp.store import MemoryBankStore


CASES_PATH = Path(__file__).with_name("search_regression.json")
REAL_CASES_PATH = Path(__file__).with_name("search_regression_real.json")
TASK_ROOT = Path(__file__).resolve().parents[1]


def markdown(
    title: str,
    *,
    identifier: str | None = None,
    aliases: list[str] | None = None,
    keywords: list[str] | None = None,
    repository: str | None = None,
    component: str | None = None,
    summary: str,
    body: str,
    doc_type: str = "architecture",
) -> str:
    lines = [
        "---",
        f"title: {title}",
        f"type: {doc_type}",
        "status: verified",
        "updated: 2026-07-30",
    ]
    if identifier:
        lines.append(f"id: {identifier}")
    if aliases:
        lines.extend(["aliases:", *(f"  - {item}" for item in aliases)])
    if keywords:
        lines.extend(["keywords:", *(f"  - {item}" for item in keywords)])
    if repository:
        lines.append(f"repository: {repository}")
    if component:
        lines.append(f"component: {component}")
    lines.extend(
        [
            "---",
            "",
            f"# {title}",
            "",
            "## Summary",
            "",
            summary,
            "",
            "## Details",
            "",
            body,
            "",
        ]
    )
    return "\n".join(lines)


class SearchTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        documents = {
            "specification.md": markdown(
                "Kafka Adapter Delivery",
                identifier="SPEC-0001",
                aliases=["адаптер доставки"],
                keywords=["KafkaAdapter", "kafka-adapter", "producer_queue"],
                repository="kafka-adapter",
                component="publisher",
                summary="Publisher retry policy and reliable Kafka delivery.",
                body="Producer queue выполняет повторную отправку сообщений.",
                doc_type="specification",
            ),
            "decision.md": markdown(
                "Markdown Canonical Storage",
                identifier="ADR-0001",
                aliases=["решение хранения"],
                keywords=["source of truth"],
                summary="Markdown is the source of truth for project knowledge.",
                body="Решение хранения не требует внешней базы данных.",
                doc_type="decision",
            ),
            "background.md": markdown(
                "Фоновая обработка",
                aliases=["фоновые задания"],
                keywords=["BackgroundWorker"],
                component="scheduler",
                summary="Фоновые задания обслуживают очереди.",
                body="BackgroundWorker запускает близко расположенные фоновые задания.",
            ),
            "consumer.md": markdown(
                "Kafka Consumer Offsets",
                keywords=["consumer_group", "consumer/group"],
                repository="kafka-adapter",
                component="consumer",
                summary="Consumer управляет смещениями группы.",
                body="Consumer offset хранится для каждой consumer group.",
            ),
            "schemas.md": markdown(
                "Schema Registry",
                aliases=["реестр схем"],
                keywords=["SchemaRegistry", "Avro"],
                component="serialization",
                summary="Avro schema compatibility and registry integration.",
                body="Реестр схем проверяет совместимость контрактов.",
            ),
            "noise.md": markdown(
                "Unrelated Operations",
                summary="Deployment and monitoring.",
                body="Health checks, dashboards, and release process.",
            ),
        }
        for name, content in documents.items():
            (self.root / name).write_text(content, encoding="utf-8")
        self.store = MemoryBankStore(self.root)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_normalizer_and_tokenizer_preserve_identifier_variants(self) -> None:
        self.assertEqual("ежик kafka adapter", normalize_text("Ёжик KafkaAdapter"))
        self.assertEqual("spec0001", normalize_identifier("SPEC-0001"))
        terms = tokenize("KafkaAdapter kafka-adapter consumer/group")
        self.assertTrue(
            {"kafkaadapter", "kafka-adapter", "kafka", "adapter"}.issubset(terms)
        )
        self.assertIn("consumer/group", terms)

    def test_regression_metrics(self) -> None:
        cases = json.loads(CASES_PATH.read_text(encoding="utf-8"))
        metrics = evaluate_search(self.store, cases)
        failures = [
            detail
            for detail in metrics["details"]
            if detail["expected"]
            and not set(detail["expected"]).intersection(detail["actual"])
        ]
        self.assertEqual([], failures)
        self.assertGreaterEqual(metrics["hit_at_1"], 0.9)
        self.assertEqual(1.0, metrics["hit_at_3"])
        self.assertGreaterEqual(metrics["mrr"], 0.95)
        self.assertEqual(1.0, metrics["no_result_accuracy"])

    def test_real_corpus_ranking_is_not_worse_than_legacy_search(self) -> None:
        cases = json.loads(REAL_CASES_PATH.read_text(encoding="utf-8"))
        real_store = MemoryBankStore(TASK_ROOT / "memory-bank")
        indexed = evaluate_search(real_store, cases)
        legacy = evaluate_search(
            real_store,
            cases,
            search=lambda query, **filters: legacy_search(
                real_store,
                query,
                **filters,
            ),
        )
        self.assertGreaterEqual(indexed["hit_at_1"], legacy["hit_at_1"])
        self.assertGreaterEqual(indexed["hit_at_3"], legacy["hit_at_3"])
        self.assertGreaterEqual(indexed["mrr"], legacy["mrr"])
        self.assertGreaterEqual(indexed["hit_at_1"], 0.9)
        self.assertEqual(1.0, indexed["hit_at_3"])

    def test_exact_id_and_field_boosts(self) -> None:
        exact = self.store.search("SPEC-0001")
        self.assertEqual("specification.md", exact["results"][0]["path"])
        self.assertEqual(
            100.0, exact["results"][0]["score_details"]["exact_id"]
        )
        alias = self.store.search("адаптер доставки")
        self.assertIn("aliases", alias["results"][0]["matched_fields"])
        keyword = self.store.search("BackgroundWorker")
        self.assertIn("keywords", keyword["results"][0]["matched_fields"])
        self.assertIn("BackgroundWorker", keyword["results"][0]["fragment"])

    def test_index_detects_change_addition_and_removal(self) -> None:
        self.assertEqual("background.md", self.store.search("BackgroundWorker")["results"][0]["path"])
        path = self.root / "background.md"
        path.write_text(
            markdown(
                "Фоновая обработка",
                summary="Задачи обслуживают очереди.",
                body="Планировщик выполняет работу.",
            ),
            encoding="utf-8",
        )
        self.assertEqual([], self.store.search("BackgroundWorker")["results"])
        added = self.root / "new.md"
        added.write_text(
            markdown(
                "New Worker",
                keywords=["BackgroundWorker"],
                summary="Replacement worker.",
                body="Replacement.",
            ),
            encoding="utf-8",
        )
        self.assertEqual("new.md", self.store.search("BackgroundWorker")["results"][0]["path"])
        added.unlink()
        self.assertEqual([], self.store.search("BackgroundWorker")["results"])

    def test_results_are_deterministic_and_bounded(self) -> None:
        first = self.store.search("Kafka", limit=2, max_chars=100_000)
        second = self.store.search("Kafka", limit=2, max_chars=100_000)
        self.assertEqual(first, second)
        self.assertLessEqual(first["count"], 2)
        tiny = self.store.search("Kafka", limit=100, max_chars=256)
        self.assertLessEqual(
            len(json.dumps(tiny, ensure_ascii=False)), 256
        )


if __name__ == "__main__":
    unittest.main()
