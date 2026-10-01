from __future__ import annotations

import argparse
import re
from pathlib import Path

import pandas as pd

REQUIRED_CANDIDATES = ("description", "category", "priority")
PII_PATTERNS = [
    re.compile(r"(?i)\b[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}\b"),
    re.compile(r"(?<!\w)(?:\+?\d[\d .()/-]{7,}\d)(?!\w)"),
    re.compile(r"\b(?:\d{1,3}\.){3}\d{1,3}\b"),
    re.compile(r"\b[0-9a-f]{8}-[0-9a-f]{4}-[1-5][0-9a-f]{3}-[89ab][0-9a-f]{3}-[0-9a-f]{12}\b", re.I),
]


def redact_text(value: object) -> str:
    text = "" if pd.isna(value) else str(value)
    for pattern in PII_PATTERNS:
        text = pattern.sub("[REDACTED]", text)
    return re.sub(r"\s+", " ", text).strip()


def split_frame(frame: pd.DataFrame, label: str, seed: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    rng = __import__("random").Random(seed)
    groups: list[list[int]] = [[], [], []]
    for _, group in frame.groupby(label, dropna=False):
        indices = list(group.index)
        rng.shuffle(indices)
        n = len(indices)
        n_test = max(1, round(n * 0.15)) if n > 2 else 0
        n_val = max(1, round(n * 0.15)) if n - n_test > 2 else 0
        groups[0].extend(indices[: n - n_test - n_val])
        groups[1].extend(indices[n - n_test - n_val : n - n_test])
        groups[2].extend(indices[n - n_test :])
    return tuple(frame.loc[idx].sample(frac=1, random_state=seed).reset_index(drop=True) for idx in groups)  # type: ignore[return-value]


def prepare(input_path: Path, output_dir: Path, seed: int = 42) -> dict[str, object]:
    frame = pd.read_csv(input_path)
    missing_fields = [name for name in REQUIRED_CANDIDATES if name not in frame.columns]
    if missing_fields:
        raise ValueError(f"CSV is missing required fields: {missing_fields}")
    before = len(frame)
    duplicates = int(frame.duplicated().sum())
    frame = frame.drop_duplicates().copy()
    for column in frame.select_dtypes(include="object").columns:
        frame[column] = frame[column].map(redact_text)
    frame["description"] = frame["description"].fillna("").str.strip()
    frame["category"] = frame["category"].str.strip()
    frame["priority"] = frame["priority"].str.strip().str.title()
    valid = (frame["description"].str.len() > 0) & (frame["category"].str.len() > 0) & (frame["priority"].str.len() > 0)
    invalid_required_rows = int((~valid).sum())
    frame = frame[valid].copy()
    # Remove row-level source identifiers from derived exports by default.
    frame = frame.drop(columns=[c for c in ("ticket_id",) if c in frame.columns])
    train, validation, test = split_frame(frame, "category", seed)
    output_dir.mkdir(parents=True, exist_ok=True)
    train.to_csv(output_dir / "train.csv", index=False)
    validation.to_csv(output_dir / "validation.csv", index=False)
    test.to_csv(output_dir / "test.csv", index=False)
    return {
        "rows_before": before,
        "rows_after": len(frame),
        "duplicates_removed": duplicates,
        "rows_with_empty_required_values_removed": invalid_required_rows,
        "columns": list(frame.columns),
        "split_rows": {"train": len(train), "validation": len(validation), "test": len(test)},
        "missing_after": {str(k): int(v) for k, v in frame.isna().sum().items()},
        "category_counts": {str(k): int(v) for k, v in frame["category"].value_counts().items()},
        "resolution_missing": int(frame["resolution"].eq("").sum()) if "resolution" in frame else None,
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Clean, redact, and split support tickets")
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, default=Path("data/processed"))
    parser.add_argument("--seed", type=int, default=42)
    args = parser.parse_args()
    print(prepare(args.input, args.output_dir, args.seed))


if __name__ == "__main__":
    main()
