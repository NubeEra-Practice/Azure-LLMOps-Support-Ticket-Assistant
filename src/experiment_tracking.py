from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def log_experiment(record: dict[str, Any], path: Path = Path("experiments/runs.jsonl")) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {"recorded_at_utc": datetime.now(timezone.utc).isoformat(), **record}
    with path.open("a", encoding="utf-8") as stream:
        stream.write(json.dumps(payload, ensure_ascii=False) + "\n")
