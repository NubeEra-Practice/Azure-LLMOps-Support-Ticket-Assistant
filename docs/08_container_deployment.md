# 08 — Containerization and deployment

Build and run after Docker is available:

```powershell
docker build -t ticket-assistant:local .
docker run --rm -p 8000:8000 --env-file .env ticket-assistant:local
```

The Dockerfile installs dependencies, runs Uvicorn, and checks `/health`. Docker was unavailable, so no build/run occurred. Azure Container Apps deployment was not attempted because the portal reported the trial expired/services paused and the brief did not state an acceptable spend ceiling.

For a later approved deployment, select a supported region/model, use Consumption with min replicas 0 and a conservative max, managed identity for Blob/Key Vault, no secrets in image layers, a budget/alert, and an estimate for vCPU/GiB seconds, requests, registry, logs, retention, and egress. CI has no deploy command.
