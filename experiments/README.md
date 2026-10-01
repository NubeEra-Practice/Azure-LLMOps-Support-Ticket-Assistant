# Experiment tracking

`src.experiment_tracking.log_experiment()` appends one JSON object per run to `experiments/runs.jsonl`. Record dataset checksum/version, split seed, prompt version, model/deployment label, evaluation metrics, duration, token counts, and estimated cost. Never write ticket descriptions, credentials, or model secrets into experiment records. The generated JSONL is git-ignored.
