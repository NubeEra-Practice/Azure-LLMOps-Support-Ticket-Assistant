# 10 — CI/CD pipeline

`.github/workflows/llmops-ci.yml` checks out code, installs Python dependencies, compiles modules, runs pytest, and builds a Docker image. It runs for push/PR to `main`, but has no paid deployment step. It was not pushed or triggered; no GitHub connection or secrets were created.

For later deployment, use protected environment approval and workload identity federation instead of a long-lived Azure secret. Add a separate manual deploy job only after budget review.
