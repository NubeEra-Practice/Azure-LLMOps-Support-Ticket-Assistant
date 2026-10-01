from fastapi.testclient import TestClient

from src import main
from src.schemas import TicketResult


class FakeProcessor:
    def classify(self, ticket):
        return TicketResult(
            ticket_id=ticket.ticket_id,
            category="Cloud Storage",
            priority="High",
            resolution_suggestion="Check container access and recent changes; escalate with redacted logs.",
            confidence=0.7,
            prompt_version="test-v1",
            model_name="fake-test-model",
        )

    def classify_batch(self, tickets):
        return [self.classify(ticket) for ticket in tickets]


def setup_function():
    main.processor = FakeProcessor()


def test_health():
    response = TestClient(main.app).get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_classify():
    response = TestClient(main.app).post(
        "/tickets/classify",
        json={"description": "Blob download returns an authorization error", "ticket_id": "redacted-demo"},
    )
    assert response.status_code == 200
    assert response.json()["category"] == "Cloud Storage"
    assert response.json()["priority"] == "High"


def test_batch_and_metrics():
    client = TestClient(main.app)
    response = client.post(
        "/tickets/batch",
        json={"tickets": [{"description": "Network DNS resolution is failing"}]},
    )
    assert response.status_code == 200
    assert response.json()["count"] == 1
    assert client.get("/metrics").json()["requests_total"] >= 1


def test_invalid_ticket_is_rejected():
    response = TestClient(main.app).post("/tickets/classify", json={"description": "short"})
    assert response.status_code == 422
