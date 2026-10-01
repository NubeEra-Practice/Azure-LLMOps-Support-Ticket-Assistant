# 09 — Monitoring and observability

The API exposes `/metrics` with process-local request counts and average/maximum latency. It avoids persisting ticket text. A hosted deployment may add Application Insights through Azure Monitor OpenTelemetry after estimating ingestion and retention; configure sampling and redact errors. Never put complete ticket descriptions into logs, traces, or metric dimensions.

No Application Insights resource, workspace, dashboard, or alert was created. `/metrics` can be inspected after local startup. Use Azure Activity Log and Cost Management for deployed-resource charges.
