# 06 — Experiment tracking

`src/experiment_tracking.py` appends JSONL records for dataset checksum/version, split seed, prompt version, model/deployment, evaluation metrics, duration, tokens, and estimated cost. Never log ticket text or secrets. Generated runs are git-ignored.

Azure Machine Learning was not provisioned. For this dataset scale, local JSONL is sufficient without leaving billable compute running. An AML workspace/compute should be introduced only after its VM-hour and dependent storage/monitoring costs are budgeted. No experiment run was recorded because Python and a real model endpoint were unavailable.
