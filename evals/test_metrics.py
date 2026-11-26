from prd_reviewer.metrics import check_metrics
from evals.scoring import load_json, evaluate_review
from prd_reviewer.schema import ReviewOutput

# 1. Load the PRD text
with open("evals/apps/seed_01.md", "r") as f:
    prd_text = f.read()

# 2. Run the metrics check
findings = check_metrics(prd_text)

# 3. Wrap it in the ReviewOutput schema
review_output = ReviewOutput(
    prd_id="seed_01",
    findings=findings
)

# 4. Load the answer key
answer_key = load_json("evals/answer_key.json")

# 5. Score it
results = evaluate_review(answer_key, review_output)

import json
print("=== METRICS PIPELINE TEST ===")
print(json.dumps(results, indent=2))
print("\n--- Raw Findings ---")
for f in findings:
    print(f"Type: {f.finding_type} | Severity: {f.severity} | Evidence: '{f.evidence[0].quote}'")