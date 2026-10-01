from __future__ import annotations

import argparse
import hashlib
import json
import statistics
import time
from pathlib import Path
from typing import Any

import pandas as pd

from src.llm_client import TicketModel
from src.schemas import TicketInput
from src.experiment_tracking import log_experiment


def class_metrics(expected: list[str], predicted: list[str]) -> dict[str, Any]:
    labels = sorted(set(expected) | set(predicted))
    per_class: dict[str, dict[str, float | int]] = {}
    weighted = {"precision": 0.0, "recall": 0.0, "f1": 0.0}
    total = len(expected)
    for label in labels:
        tp = sum(a == label and b == label for a, b in zip(expected, predicted))
        fp = sum(a != label and b == label for a, b in zip(expected, predicted))
        fn = sum(a == label and b != label for a, b in zip(expected, predicted))
        support = sum(a == label for a in expected)
        precision = tp / (tp + fp) if tp + fp else 0.0
        recall = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * precision * recall / (precision + recall) if precision + recall else 0.0
        per_class[label] = {"precision": precision, "recall": recall, "f1": f1, "support": support}
        for metric, value in (("precision", precision), ("recall", recall), ("f1", f1)):
            weighted[metric] += value * support / total if total else 0.0
    accuracy = sum(a == b for a, b in zip(expected, predicted)) / total if total else None
    return {"accuracy": accuracy, "weighted": weighted, "per_class": per_class, "n": total}


def evaluate(path: Path, output: Path, max_rows: int | None = None) -> dict[str, Any]:
    run_started = time.perf_counter()
    frame = pd.read_csv(path)
    required = {"description", "category", "priority"}
    if not required.issubset(frame.columns):
        raise ValueError(f"Evaluation data must contain {sorted(required)}")
    if max_rows:
        frame = frame.head(max_rows)
    model = TicketModel()
    category_expected: list[str] = []
    category_predicted: list[str] = []
    priority_expected: list[str] = []
    priority_predicted: list[str] = []
    latencies: list[float] = []
    valid_json = 0
    for _, row in frame.iterrows():
        ticket = TicketInput(
            description=str(row["description"]),
            current_priority=None,
            product=str(row.get("product", "")) or None,
            region=str(row.get("region", "")) or None,
        )
        start = time.perf_counter()
        result = model.classify(ticket)
        latencies.append((time.perf_counter() - start) * 1000)
        # Pydantic output validation happened in TicketModel.classify; count only valid objects.
        valid_json += 1
        category_expected.append(str(row["category"]))
        category_predicted.append(result.category)
        priority_expected.append(str(row["priority"]).title())
        priority_predicted.append(result.priority)
    payload = {
        "status": "completed",
        "mode": "offline" if model.offline else "azure_openai",
        "model_name": "offline-rules-v1" if model.offline else model.deployment,
        "prompt_version": model.prompt_version,
        "rows_evaluated": len(frame),
        "category": class_metrics(category_expected, category_predicted),
        "priority": class_metrics(priority_expected, priority_predicted),
        "json_validity_rate": valid_json / len(frame) if len(frame) else None,
        "latency_ms": {
            "median": statistics.median(latencies) if latencies else None,
            "p95": sorted(latencies)[max(0, int(len(latencies) * 0.95) - 1)] if latencies else None,
        },
        "token_usage": model.usage_snapshot(),
        "estimated_inference_cost_usd": model.usage_snapshot().get("estimated_cost_usd"),
        "cost_note": "Offline rules use no model tokens." if model.offline else "Rates must be supplied in the environment and verified for the deployment region.",
        "warning": "Offline rule baseline is not an LLM result." if model.offline else None,
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(payload, indent=2), encoding="utf-8")
    log_experiment({
        "dataset_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
        "prompt_version": model.prompt_version,
        "model_name": payload["model_name"],
        "mode": payload["mode"],
        "rows_evaluated": len(frame),
        "category_accuracy": payload["category"]["accuracy"],
        "priority_accuracy": payload["priority"]["accuracy"],
        "duration_seconds": round(time.perf_counter() - run_started, 3),
        "token_usage": payload["token_usage"],
        "estimated_cost_usd": payload["estimated_inference_cost_usd"],
    })
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description="Evaluate category/priority against labeled tickets")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("evaluation/results.json"))
    parser.add_argument("--max-rows", type=int)
    args = parser.parse_args()
    print(json.dumps(evaluate(args.input, args.output, args.max_rows), indent=2))


if __name__ == "__main__":
    main()
