# 03 — Resource inventory and cost plan

No Azure resources were provisioned, resized, paused, or deleted. The portal reported the free trial expired/services paused and did not show a usable remaining credit balance.

| Resource | Observed / proposed | Cost model and estimate status |
|---|---|---|
| `sanginx001` Storage Account | Existing, Qatar Central; retain | Hot blob capacity, reads/writes, and transfer are metered; exact usage/credit was not visible. The portal download was 3.04 MiB. Any read/transfer charge is expected to be small but is not asserted as zero. |
| `azure-llmops-search` | Existing, Running, Standard; 1 replica × 1 partition (1 SU) | Fixed hourly Search Unit cost; potentially material recurring spend. Verify exact region/currency in Cost Analysis or calculator. Not modified. |
| Azure OpenAI | Not present; optional | Pay-as-you-go model/token rates or reserved PTU capacity; depends on model, deployment type, region, and actual input/output tokens. No deployment/calls; project inference cost $0. |
| Azure Machine Learning | Not present; omitted | Compute VM hours plus dependent storage/monitoring can dominate. Local JSONL tracking is used instead. |
| Azure Container Apps | Not present; optional | Consumption plan grants 180,000 vCPU-seconds, 360,000 GiB-seconds, and 2 million requests per subscription/month; above those, usage is metered. Scale to zero. No app deployed. |
| Application Insights / Azure Monitor | Not present; optional | Ingestion, retention, export, alerts, and metrics can incur charges. No workspace created. |
| GitHub Actions | Workflow file only | Runs under the user's GitHub plan/quota if committed. Nothing was pushed or triggered. |

## Cost gate

Before any cloud deployment: verify subscription state/credits and cost alerts; select the model and allowed region; calculate monthly tokens, Container Apps active seconds, telemetry/retention, registry, and egress in the official calculator; then obtain approval if expected charges are material. The brief supplies no numeric spend ceiling, so no billable resource was created.

Current references: [Azure OpenAI pricing](https://azure.microsoft.com/en-us/pricing/details/cognitive-services/openai-service/), [Container Apps pricing](https://azure.microsoft.com/en-us/pricing/details/container-apps/), [Azure Monitor pricing](https://azure.microsoft.com/en-us/pricing/details/monitor/), [Blob pricing](https://azure.microsoft.com/en-us/pricing/details/storage/blobs/), [Search tier/billing model](https://learn.microsoft.com/en-us/azure/search/search-sku-tier), [Azure pricing calculator](https://azure.microsoft.com/en-us/pricing/calculator/).

Exact deployment estimates were not available because no model/compute configuration or acceptable budget was selected, and the portal did not provide a usable credit balance. This does not mean the existing Search resource is free.
