from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


Priority = Literal["Critical", "High", "Medium", "Low"]
Category = Literal[
    "Account Access", "AI Services", "Billing", "Cloud Storage", "Compute", "Networking"
]


class TicketInput(BaseModel):
    model_config = ConfigDict(extra="forbid")

    ticket_id: str | None = Field(default=None, max_length=80)
    description: str = Field(min_length=8, max_length=8000)
    product: str | None = Field(default=None, max_length=120)
    region: str | None = Field(default=None, max_length=80)
    current_priority: Priority | None = None

    @field_validator("description")
    @classmethod
    def description_not_blank(cls, value: str) -> str:
        if not value.strip():
            raise ValueError("description cannot be blank")
        return value.strip()


class TicketResult(BaseModel):
    ticket_id: str | None = None
    category: Category
    priority: Priority
    resolution_suggestion: str = Field(min_length=1, max_length=2000)
    confidence: float = Field(ge=0.0, le=1.0)
    prompt_version: str
    model_name: str


class BatchTicketInput(BaseModel):
    tickets: list[TicketInput] = Field(min_length=1, max_length=50)


class BatchTicketResult(BaseModel):
    results: list[TicketResult]
    count: int


class HealthResponse(BaseModel):
    status: Literal["ok"]
    mode: Literal["offline", "azure_openai"]

