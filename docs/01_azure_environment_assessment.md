# 01 — Azure environment assessment

Assessment date: 2026-10-01. Observations came from the authenticated Azure Portal; free-text ticket values were not copied into this report.

## Subscription and resources

- Subscription: `Az28SepDmp` (`b3160472-ba02-4479-9a0e-c291e84b959f`), `Default Directory`.
- Portal home said the free trial had expired, services were paused, and the account was scheduled for deletion on 31 October 2026 unless upgraded. The subscription overview separately showed 58 unused free-service offers, but no remaining $200 credit balance. Treat deployable trial credit as **unverified / unavailable**.
- Resource group `rg-nginx` is located in East US and contains two resources, both located in Qatar Central:
  - `sanginx001` Storage account, existing.
  - `azure-llmops-search` Azure AI Search / Foundry IQ, existing, Running, Standard tier, 1 replica × 1 partition = 1 Search Unit.
- No Azure OpenAI resource/model deployment, Azure Machine Learning workspace, Container App, or Application Insights resource was listed in `rg-nginx`.
- The Standard Search service has dedicated provisioned capacity. Microsoft documents fixed hourly Search Unit billing; exact regional rate was not visible in the overview. Cost Management should be checked before deciding whether it is still needed. It was not changed.

## Storage and dataset

- `sanginx001`, Qatar Central; private container `data`; blob `azure_llmops_support_tickets.csv`, Block Blob, Hot (inferred), 3,192,604 bytes (3.04 MiB), server encrypted.
- Azure's editor rejected the 3.19 MB file because it exceeds the editor's 2.1 MB limit. The authenticated portal Download action succeeded; only a local scratch copy was used. The cloud blob was not modified.
- Dataset field counts and quality findings are in [04_data_quality_report.md](04_data_quality_report.md). The ZIP excludes the source CSV and ticket free text.

## Model, region, and cost posture

No Azure OpenAI deployment was found. Foundry model availability varies by model and deployment type, so Qatar Central availability must be confirmed in the portal for the selected model at deployment time. No model was deployed or invoked. No resources were created or modified for this project. An existing Standard Search unit is running and may continue accruing charges; see [03_azure_resources.md](03_azure_resources.md).
