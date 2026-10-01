# 11 — End-to-end demonstration status

## Completed

1. Opened Azure Portal and verified subscription, `rg-nginx`, `sanginx001`, private container `data`, and the requested blob.
2. Downloaded the blob through the authenticated portal and inspected size, fields, missingness, label distribution, cardinality, exact duplicates, and a limited PII-pattern scan locally.
3. Confirmed no Azure OpenAI deployment exists in the resource group and identified the existing Running Standard Azure AI Search service (one Search Unit).
4. Authored ingestion, preprocessing, prompt versions, offline/Azure model client, structured schemas, FastAPI, metrics, evaluation CLI, tests, Dockerfile, documentation, and CI workflow.
5. Calculated full-source offline rule-baseline category/priority metrics with the included Node.js parity harness. These are diagnostic only, not held-out or LLM results.
6. No cloud resources changed, no model calls made, no GitHub workflow triggered.

## Not executed / blockers

- Python was not configured, so preprocessing, API tests, server, model evaluation, and Python syntax checks were not run.
- Docker was unavailable; image build/run and health endpoint tests were not run.
- No Azure OpenAI deployment existed; no LLM outputs or model-token costs were measured. The offline baseline used zero tokens.
- No resources were provisioned because the portal reported the free trial expired/services paused and no numerical spend limit was supplied.
- Genuine screenshots were visible in browser control but could not be exported into project files by the available browser tool. Screenshot phase folders explain this; no fake images are included.
- The original CSV/free text are excluded for privacy. `evaluation/test_dataset.csv` is header-only until local preprocessing is run.

`evaluation/results.json` contains the offline rules diagnostic; API, Python evaluator, Docker, and hosted LLM metrics remain unexecuted.
