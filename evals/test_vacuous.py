from prd_reviewer.scope import check_scope

# Read the bad PRD
with open("evals/apps/seed_vacuous.md", "r") as f:
    prd_text = f.read()

print("Sending PRD to Qwen...")
findings = check_scope(prd_text)

print("\n=== MODEL OUTPUT ===")
if not findings:
    print("The model found no issues (or the API failed).")
else:
    for f in findings:
        print(f"✅ Found: {f.finding_type}")
        print(f"   Severity: {f.severity}")
        print(f"   Evidence: '{f.evidence[0].quote}'")
        print(f"   Issue: {f.issue}")