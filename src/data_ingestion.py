from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def fetch_blob(container_url: str, blob_name: str, output: Path) -> None:
    """Download a private blob using Azure DefaultAzureCredential (no account keys)."""
    from azure.identity import DefaultAzureCredential
    from azure.storage.blob import BlobClient

    credential = DefaultAzureCredential()
    blob = BlobClient.from_blob_url(
        f"{container_url.rstrip('/')}/{blob_name.lstrip('/')}", credential=credential
    )
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("wb") as target:
        target.write(blob.download_blob().readall())


def validate_csv(path: Path) -> dict[str, object]:
    frame = pd.read_csv(path)
    if frame.empty:
        raise ValueError("CSV contains no rows")
    return {
        "rows": int(len(frame)),
        "columns": list(frame.columns),
        "duplicate_rows": int(frame.duplicated().sum()),
        "missing_by_column": {str(k): int(v) for k, v in frame.isna().sum().items()},
    }


def main() -> None:
    parser = argparse.ArgumentParser(description="Fetch and inspect the support-ticket CSV")
    parser.add_argument("--input-csv", type=Path)
    parser.add_argument("--container-url", help="Container URL; auth uses DefaultAzureCredential")
    parser.add_argument("--blob-name", default="azure_llmops_support_tickets.csv")
    parser.add_argument("--output-csv", type=Path, default=Path("data/working/tickets.csv"))
    args = parser.parse_args()
    if args.input_csv:
        source = args.input_csv
        if not source.is_file():
            parser.error(f"input CSV does not exist: {source}")
        args.output_csv.parent.mkdir(parents=True, exist_ok=True)
        if source.resolve() != args.output_csv.resolve():
            args.output_csv.write_bytes(source.read_bytes())
    elif args.container_url:
        source = args.output_csv
        fetch_blob(args.container_url, args.blob_name, source)
    else:
        parser.error("provide --input-csv or --container-url")
    print(validate_csv(source))


if __name__ == "__main__":
    main()
