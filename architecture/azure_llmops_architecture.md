# Architecture

```mermaid
flowchart LR
  B[Existing Azure Blob CSV] --> I[Ingestion with Entra identity]
  I --> P[Validate, redact, preprocess, split]
  P --> E[Evaluation and prompt comparison]
  P --> A[FastAPI ticket API]
  A --> T[Ticket processor and versioned prompts]
  T --> M{Model mode}
  M -->|Local demo| R[Deterministic offline rules]
  M -->|Configured, metered| O[Azure OpenAI deployment]
  R --> J[Validated JSON response]
  O --> J
  A --> L[Local request metrics]
  L -. optional, billable ingestion .-> AI[Application Insights / Azure Monitor]
  E --> X[Local JSONL experiment records]
  G[GitHub Actions] --> C[Tests and container build]
  C -. manual approval and cost gate .-> ACA[Azure Container Apps, scale to zero]
```

The current demonstration path is local/offline. Azure OpenAI, Application Insights, and Container Apps are optional integration points and were not provisioned. The existing Azure AI Search service is not required for this small classification demo and remains untouched.
