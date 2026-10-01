# 05 — Prompt engineering and evaluation

`src/prompts.py` implements `zero-shot-v1`, `few-shot-v1`, and `structured-v1`; fictional few-shot examples are labelled synthetic. `PROMPT_VERSION` selects the prompt. JSON is parsed and validated by Pydantic.

An honest deterministic offline-rules baseline was calculated over all 12,000 labeled source rows with a local Node.js parity harness matching the rules in `src/llm_client.py`: category accuracy 0.6763 / weighted F1 0.6849; priority accuracy 0.4862 / weighted F1 0.3527. These are full-source diagnostic scores, not held-out results and not LLM performance. The low priority score shows the offline heuristic is not suitable for operational triage. Source rows and text are not included in the ZIP. There was no configured Python runtime or Azure OpenAI deployment, so the Python evaluator, API JSON validation, latency, and model evaluation were not run. Details and limitations are in `evaluation/results.json`.

The aggregate baseline can be reproduced without printing row text: `node evaluation/offline_baseline_audit.cjs path/to/source.csv`.

After preprocessing, run `python -m evaluation.evaluate --input data/processed/test.csv --output evaluation/results.json`. The offline mode measures only deterministic rules and must be labelled non-LLM. For model evaluation, configure Azure OpenAI, record actual model/token usage and regional rates, and compare prompt versions over the same held-out data. Do not pass `topic` as a category feature if it reveals the answer. Because text templates repeat, add a time/grouped holdout before making production claims.

The Python evaluator computes accuracy, weighted/per-class precision/recall/F1, JSON validity, and latency. Offline token use/cost is zero; online cost remains null unless actual token counts and applicable rates are supplied. Run it on the generated test split before treating the current diagnostic as a model evaluation.
