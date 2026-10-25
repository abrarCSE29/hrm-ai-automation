"""Placeholder eval runner (not wired to a real LLM in CI)."""

import json
import os

cases_path = os.path.join(os.path.dirname(__file__), "..", "evals", "cases.jsonl")
with open(cases_path) as f:
    cases = [json.loads(line) for line in f if line.strip()]
print(f"Loaded {len(cases)} eval cases (runner is a placeholder).")
for c in cases:
    print("-", c.get("name"))
