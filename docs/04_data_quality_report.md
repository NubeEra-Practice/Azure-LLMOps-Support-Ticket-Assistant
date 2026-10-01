# 04 — Data quality and privacy report

Source: `rg-nginx / sanginx001 / data / azure_llmops_support_tickets.csv`, inspected on 2026-10-01. Original CSV and free-text bodies/resolutions are excluded from the ZIP.

## Shape and quality

- 12,000 rows; 11 columns; 3,192,604 bytes.
- No exact duplicate full rows (12,000 distinct records).
- `ticket_id`, `created_at`, `category`, `topic`, `product`, `region`, `priority`, `status`, `customer_tier`, and `description` are complete.
- `resolution` is present for 7,836 rows and missing for 4,164 (34.7%). Do not use missing-resolution rows as supervised resolution targets.
- Max text lengths: `description` 111 chars; `resolution` 103 chars. Text itself is intentionally omitted from this report.
- Basic scans found no email, phone-number, or IPv4 patterns in description/resolution. This limited scan cannot guarantee absence of names, identifiers, or other sensitive context.

## Cardinality and label distribution

| Field | Distinct | Counts |
|---|---:|---|
| `category` | 6 | Account Access 2,014; AI Services 2,064; Billing 1,973; Cloud Storage 2,000; Compute 2,017; Networking 1,932 |
| `priority` | 4 | Critical 850; High 3,338; Low 1,814; Medium 5,998 |
| `topic` | 24 | 24 values |
| `product` | 6 | 6 values |
| `region` | 5 | 5 values |
| `status` | 4 | 4 values |
| `customer_tier` | 4 | 4 values |

Other cardinality: `ticket_id` 12,000; `created_at` 11,940. `description` has 18 unique values and `resolution` has 5 unique non-empty values, suggesting repeated templates; random splits can overstate generalization. Use time-based or near-duplicate-grouped holdouts for a stronger follow-up.

## Metadata-only sample rows

| Category | Topic | Priority | Description chars | Resolution present |
|---|---|---|---:|---|
| AI Services | model deployment | High | 87 | No |
| Compute | VM startup failure | Low | 75 | No |
| AI Services | vector indexing | Medium | 78 | No |
| Cloud Storage | storage quota | Critical | 100 | No |
| Cloud Storage | file permissions | High | 59 | Yes |

No row IDs, ticket text, or resolutions are included. One sampled row paired AI Services with an Azure Blob Storage product, and another paired AI Services with Azure Virtual Machines. Treat `product` as noisy context, not ground truth.

## Preparation

`src/data_preprocessing.py` validates `description`, `category`, `priority`; removes exact duplicates; normalizes whitespace/labels; masks common emails, phone numbers, IPv4 addresses, and UUIDs; drops `ticket_id`; and writes seeded train/validation/test CSVs. It does not claim comprehensive PII detection. Review output before sharing and keep source CSV out of git/screenshots.

No processed split is included because Python was not configured and full ticket text was intentionally kept outside this archive. Run the provided scripts locally after reviewing privacy requirements.
