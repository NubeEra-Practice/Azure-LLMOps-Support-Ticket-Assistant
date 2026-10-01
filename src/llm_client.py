from __future__ import annotations

import json
import os
import re
import time
from typing import Any

from .prompts import PROMPT_VERSION, SYSTEM_PROMPTS, USER_TEMPLATE
from .schemas import TicketInput, TicketResult


class ModelConfigurationError(RuntimeError):
    pass


class TicketModel:
    """Azure OpenAI client with an explicit deterministic offline demonstration mode."""

    def __init__(self) -> None:
        endpoint = os.getenv("AZURE_OPENAI_ENDPOINT", "").strip()
        deployment = os.getenv("AZURE_OPENAI_DEPLOYMENT", "").strip()
        self.prompt_version = os.getenv("PROMPT_VERSION", PROMPT_VERSION)
        self.offline = os.getenv("APP_MODE", "offline").lower() == "offline"
        self.deployment = deployment
        self._client: Any = None
        self._usage = {"prompt_tokens": 0, "completion_tokens": 0, "estimated_cost_usd": 0.0}
        if self.offline:
            return
        if not endpoint or not deployment:
            raise ModelConfigurationError(
                "Set APP_MODE=offline or configure AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_DEPLOYMENT."
            )
        from openai import AzureOpenAI

        kwargs: dict[str, Any] = {
            "azure_endpoint": endpoint,
            "api_version": os.getenv("AZURE_OPENAI_API_VERSION", "2024-10-21"),
        }
        key = os.getenv("AZURE_OPENAI_API_KEY", "").strip()
        if key:
            kwargs["api_key"] = key
        elif os.getenv("AZURE_OPENAI_USE_ENTRA", "false").lower() == "true":
            from azure.identity import DefaultAzureCredential, get_bearer_token_provider

            provider = get_bearer_token_provider(
                DefaultAzureCredential(), "https://cognitiveservices.azure.com/.default"
            )
            kwargs["azure_ad_token_provider"] = provider
        else:
            raise ModelConfigurationError(
                "Provide AZURE_OPENAI_API_KEY or set AZURE_OPENAI_USE_ENTRA=true with an authenticated identity."
            )
        self._client = AzureOpenAI(**kwargs)

    @staticmethod
    def _offline_result(ticket: TicketInput) -> dict[str, Any]:
        text = " ".join(filter(None, [ticket.description, ticket.product])).lower()
        rules = [
            ("Account Access", ("login", "sign in", "password", "account", "access", "mfa")),
            ("AI Services", ("model", "prompt", "token", "inference", "ai service", "deployment")),
            ("Billing", ("bill", "invoice", "charge", "payment", "cost", "quota")),
            ("Cloud Storage", ("blob", "storage", "container", "upload", "file", "disk")),
            ("Networking", ("network", "dns", "firewall", "connectivity", "route", "endpoint")),
            ("Compute", ("vm", "compute", "cpu", "memory", "instance", "container app")),
        ]
        category = next((name for name, terms in rules if any(t in text for t in terms)), "Compute")
        critical_terms = ("outage", "production down", "data loss", "security breach")
        high_terms = ("blocked", "unavailable", "failed", "cannot access", "can't access")
        priority = ticket.current_priority or (
            "Critical" if any(t in text for t in critical_terms) else
            "High" if any(t in text for t in high_terms) else "Medium"
        )
        return {
            "category": category,
            "priority": priority,
            "resolution_suggestion": (
                "Confirm the affected service and scope, check recent configuration changes and service health, "
                "then follow the product runbook. Avoid sharing credentials; escalate with redacted diagnostics if unresolved."
            ),
            "confidence": 0.35,
        }

    def classify(self, ticket: TicketInput) -> TicketResult:
        if self.offline:
            payload = self._offline_result(ticket)
            model_name = "offline-rules-v1"
            self.last_usage = {"prompt_tokens": 0, "completion_tokens": 0, "estimated_cost_usd": 0.0}
        else:
            system = SYSTEM_PROMPTS.get(self.prompt_version, SYSTEM_PROMPTS[PROMPT_VERSION])
            user = USER_TEMPLATE.format(
                description=ticket.description,
                product=ticket.product or "not specified",
                region=ticket.region or "not specified",
                priority=ticket.current_priority or "not specified",
            )
            from openai import APIConnectionError, APITimeoutError, InternalServerError, RateLimitError

            retryable = (APIConnectionError, APITimeoutError, InternalServerError, RateLimitError)
            for attempt in range(3):
                try:
                    response = self._client.chat.completions.create(
                        model=self.deployment,
                        temperature=0,
                        response_format={"type": "json_object"},
                        messages=[{"role": "system", "content": system}, {"role": "user", "content": user}],
                        timeout=30,
                    )
                    break
                except retryable:
                    if attempt == 2:
                        raise
                    time.sleep(0.5 * (2 ** attempt))
            content = response.choices[0].message.content or "{}"
            payload = json.loads(content)
            model_name = self.deployment
            usage = response.usage
            prompt_tokens = int(getattr(usage, "prompt_tokens", 0) or 0)
            completion_tokens = int(getattr(usage, "completion_tokens", 0) or 0)
            input_rate = os.getenv("INPUT_USD_PER_1M_TOKENS", "").strip()
            output_rate = os.getenv("OUTPUT_USD_PER_1M_TOKENS", "").strip()
            estimated = None
            if input_rate and output_rate:
                estimated = (prompt_tokens * float(input_rate) + completion_tokens * float(output_rate)) / 1_000_000
            self.last_usage = {
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "estimated_cost_usd": estimated,
            }
            self._usage["prompt_tokens"] += prompt_tokens
            self._usage["completion_tokens"] += completion_tokens
            if estimated is None:
                self._usage["estimated_cost_usd"] = None
            elif self._usage["estimated_cost_usd"] is not None:
                self._usage["estimated_cost_usd"] += estimated
        # Pydantic validates both online JSON and the offline result against the public contract.
        return TicketResult(
            ticket_id=ticket.ticket_id,
            category=payload["category"],
            priority=payload["priority"],
            resolution_suggestion=re.sub(r"\s+", " ", payload["resolution_suggestion"]).strip(),
            confidence=payload["confidence"],
            prompt_version=self.prompt_version if not self.offline else "offline-rules-v1",
            model_name=model_name,
        )

    def usage_snapshot(self) -> dict[str, int | float | None]:
        return dict(self._usage)
