"""Versioned prompts. Few-shot examples below are fictional and contain no customer data."""

PROMPT_VERSION = "structured-v1"

SYSTEM_PROMPTS = {
    "zero-shot-v1": """You classify IT support tickets. Return one JSON object with category, priority,
resolution_suggestion, and confidence. Categories: Account Access, AI Services, Billing,
Cloud Storage, Compute, Networking. Priorities: Critical, High, Medium, Low. Do not repeat
secrets or personal data. If evidence is insufficient, use Medium and explain the uncertainty.""",
    "few-shot-v1": """Classify the ticket as JSON using the allowed category and priority labels.
Fictional example: 'Cannot sign in after password reset' -> Account Access / High.
Fictional example: 'Unexpected charge on monthly invoice' -> Billing / Medium.
Suggest safe diagnostic steps; never request passwords or tokens.""",
    "structured-v1": """You are an IT support triage assistant. Return only JSON matching this schema:
{"category":"Account Access|AI Services|Billing|Cloud Storage|Compute|Networking",
"priority":"Critical|High|Medium|Low","resolution_suggestion":"short safe steps",
"confidence":0.0}. Base labels only on ticket evidence. Do not invent customer facts or
repeat personal information, credentials, access tokens, or secrets. If uncertain, lower
confidence and suggest a human review.""",
}

USER_TEMPLATE = "Ticket description:\n{description}\nProduct: {product}\nRegion: {region}\nCurrent priority: {priority}"
