from .llm_client import TicketModel
from .schemas import TicketInput, TicketResult


class TicketProcessor:
    def __init__(self, model: TicketModel | None = None) -> None:
        self.model = model or TicketModel()

    def classify(self, ticket: TicketInput) -> TicketResult:
        return self.model.classify(ticket)

    def classify_batch(self, tickets: list[TicketInput]) -> list[TicketResult]:
        return [self.classify(ticket) for ticket in tickets]
