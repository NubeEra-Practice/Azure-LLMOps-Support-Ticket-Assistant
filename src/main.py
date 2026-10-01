from __future__ import annotations

import logging
import os
from time import perf_counter

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException

from .llm_client import ModelConfigurationError
from .monitoring import RequestMetrics, elapsed_ms
from .schemas import BatchTicketInput, BatchTicketResult, HealthResponse, TicketInput, TicketResult
from .ticket_processor import TicketProcessor

logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
load_dotenv()
logger = logging.getLogger("ticket-assistant")
app = FastAPI(title="IT Support Ticket Assistant", version="1.0.0")
metrics = RequestMetrics()
processor: TicketProcessor | None = None


def get_processor() -> TicketProcessor:
    global processor
    if processor is None:
        try:
            processor = TicketProcessor()
        except ModelConfigurationError as exc:
            raise HTTPException(status_code=503, detail=str(exc)) from exc
    return processor


@app.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    mode = "offline" if os.getenv("APP_MODE", "offline").lower() == "offline" else "azure_openai"
    return HealthResponse(status="ok", mode=mode)


@app.post("/tickets/classify", response_model=TicketResult)
def classify(ticket: TicketInput) -> TicketResult:
    started = perf_counter()
    try:
        active = get_processor()
        before = active.model.usage_snapshot() if hasattr(active.model, "usage_snapshot") else None
        result = active.classify(ticket)
        after = active.model.usage_snapshot() if hasattr(active.model, "usage_snapshot") else None
        usage = {key: after[key] - before[key] for key in ("prompt_tokens", "completion_tokens")} if before and after else None
        if usage is not None:
            old_cost, new_cost = before.get("estimated_cost_usd"), after.get("estimated_cost_usd")
            usage["estimated_cost_usd"] = None if old_cost is None or new_cost is None else new_cost - old_cost
        metrics.observe("classify", elapsed_ms(started), usage=usage)
        return result
    except HTTPException:
        metrics.observe("classify", elapsed_ms(started), "configuration_error")
        raise
    except Exception as exc:
        logger.error("Ticket classification failed (%s)", type(exc).__name__)
        metrics.observe("classify", elapsed_ms(started), "error")
        raise HTTPException(status_code=502, detail="Ticket classification failed; see redacted server logs.") from exc


@app.post("/tickets/batch", response_model=BatchTicketResult)
def classify_batch(batch: BatchTicketInput) -> BatchTicketResult:
    started = perf_counter()
    try:
        active = get_processor()
        before = active.model.usage_snapshot() if hasattr(active.model, "usage_snapshot") else None
        results = active.classify_batch(batch.tickets)
        after = active.model.usage_snapshot() if hasattr(active.model, "usage_snapshot") else None
        usage = {key: after[key] - before[key] for key in ("prompt_tokens", "completion_tokens")} if before and after else None
        if usage is not None:
            old_cost, new_cost = before.get("estimated_cost_usd"), after.get("estimated_cost_usd")
            usage["estimated_cost_usd"] = None if old_cost is None or new_cost is None else new_cost - old_cost
        metrics.observe("batch", elapsed_ms(started), usage=usage)
        return BatchTicketResult(results=results, count=len(results))
    except HTTPException:
        metrics.observe("batch", elapsed_ms(started), "configuration_error")
        raise
    except Exception as exc:
        logger.error("Batch classification failed (%s)", type(exc).__name__)
        metrics.observe("batch", elapsed_ms(started), "error")
        raise HTTPException(status_code=502, detail="Batch classification failed; see redacted server logs.") from exc


@app.get("/metrics")
def get_metrics() -> dict[str, int | float | None]:
    return metrics.snapshot()
