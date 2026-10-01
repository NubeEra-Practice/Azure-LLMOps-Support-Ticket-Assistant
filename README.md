# Azure LLMOps Support Ticket Assistant

An end-to-end reference project for preparing support-ticket CSV data, classifying tickets, generating resolution suggestions, exposing a FastAPI API, evaluating prompts, and tracking lightweight experiments.

## Current execution status

- The Azure source file was read from `rg-nginx/sanginx001/data/azure_llmops_support_tickets.csv` through the authenticated Azure Portal and copied to a local scratch file for inspection. The source CSV is intentionally not included in this ZIP.
- The inspected file has 12,000 rows and 11 columns. `resolution` is blank in 4,164 rows (34.7%). Category and priority fields are complete.
- The subscription overview says the free trial has expired and services are paused; the existing `azure-llmops-search` resource is nevertheless **Running**, Standard tier, 1 replica × 1 partition in Qatar Central. No Azure resources were created or modified for this project.
- No Azure OpenAI resource/model deployment was found in `rg-nginx`; the only listed resources are that Search service and the existing storage account. The sample application defaults to a clearly labelled, deterministic offline baseline until a real model endpoint is configured.
- The offline rules were audited against the complete source CSV with the included Node.js parity harness. It reported 67.6% category accuracy and 48.6% priority accuracy; this is a diagnostic baseline on the full source, not held-out or LLM performance.
- This workstation has Node.js but no configured Python runtime, Docker, or Python packages. The Python source and tests are included, but the Python test suite, local FastAPI run, Docker build, and live model evaluation were not executed here. `evaluation/results.json` records this honestly; it does not claim model metrics.
- Portal screenshots could be viewed during the session, but this browser tool did not expose a way to save captured images into the project directory. Screenshot folders contain `README.md` notes instead of fabricated images.

## Quick start

Use Python 3.11 or 3.12, install `requirements.txt`, then:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
Copy-Item .env.example .env
python -m src.data_ingestion --input-csv C:\path\to\azure_llmops_support_tickets.csv --output-csv data\working\tickets.csv
python -m src.data_preprocessing --input data\working\tickets.csv --output-dir data\processed
python -m evaluation.evaluate --input data\processed\test.csv --offline
uvicorn src.main:app --reload
```

To reproduce only the privacy-safe aggregate offline baseline without Python, run `node evaluation/offline_baseline_audit.cjs C:\path\to\azure_llmops_support_tickets.csv`. It prints only aggregate metrics and a metadata-only one-row summary; it does not print ticket text.

Open `http://127.0.0.1:8000/docs` for the API. The offline mode is a rules-based demonstration, not an LLM. To call Azure OpenAI, configure `AZURE_OPENAI_ENDPOINT`, `AZURE_OPENAI_DEPLOYMENT`, and either `AZURE_OPENAI_API_KEY` or an authenticated Azure identity. Do not commit `.env` or credentials.

## Project map

- `src/`: ingestion, privacy-aware preprocessing, prompts, Azure OpenAI/offline client, API schemas, FastAPI app, and metrics.
- `evaluation/`: reproducible evaluation CLI and a results file reflecting the current unavailable model/runtime state.
- `experiments/`: lightweight JSONL experiment tracking format.
- `docs/`: assessment, architecture, cost, API, deployment, monitoring, CI/CD, and demo notes.
- `architecture/`: editable architecture source and PNG diagram.
- `screenshots/`: requested phase folders; see their README files for capture status.

## Cost controls

No cloud provisioning is included in this deliverable. Azure Container Apps, model calls, Azure Monitor ingestion, and Search are usage or capacity billed according to their current region and configuration. The currently running Standard Search service has a fixed hourly Search Unit charge. Verify current credits, actual meter rates, and the Search resource's continued need in the Azure cost analysis blade before any paid action. This project does not automatically deploy or call a paid model.

## Privacy

The full input CSV is not distributed in the ZIP. The preprocessing script redacts common email, phone, IP address, and UUID patterns and removes ticket identifiers from derived exports by default. This is a practical scrub, not a guarantee that all personal information in free text is detected. Review derived records before sharing them.
