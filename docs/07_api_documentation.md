# 07 — FastAPI API

Run `uvicorn src.main:app --reload`; Swagger UI is `/docs`, ReDoc is `/redoc`.

| Method | Path | Purpose |
|---|---|---|
| GET | `/health` | Readiness and selected mode |
| POST | `/tickets/classify` | Classify one validated ticket |
| POST | `/tickets/batch` | Process 1–50 tickets |
| GET | `/metrics` | In-process request count and latency summary |

Example request: `{"ticket_id":"demo-redacted-01","description":"Blob download fails with an authorization error","product":"Azure Storage","region":"East US"}`.

The response includes category, priority, resolution suggestion, confidence, prompt version, and model label. Offline mode is deterministic rules with low confidence, not an LLM. Invalid input gets 422. Model/configuration failures return generic errors; logs avoid ticket text. Tests cover health, single, batch, metrics, and invalid input, but were authored and not run because this machine has no Python runtime.
