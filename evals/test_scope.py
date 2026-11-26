from prd_reviewer.scope import check_scope
from evals.scoring import load_json, evaluate_review
from prd_reviewer.schema import ReviewOutput
import json

with open("evals/apps/seed_01.md", "r") as f:
    prd_text = f.read()

findings = check_scope(prd_text)

review_output = ReviewOutput(
    prd_id="seed_01",
    findings=findings
)

answer_key = load_json("evals/answer_key.json")
results = evaluate_review(answer_key, review_output)

print("=== SCOPE PIPELINE TEST ===")
print(json.dumps(results, indent=2))
print("\n--- Raw Findings ---")
for f in findings:
    print(f"Type: {f.finding_type} | Severity: {f.severity} | Evidence: '{f.evidence[0].quote}'")