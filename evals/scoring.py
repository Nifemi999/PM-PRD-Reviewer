import json
from typing import List, Dict, Any
from prd_reviewer.schema import ReviewOutput, Finding

def load_json(path: str) -> dict:
    with open(path, "r") as f:
        return json.load(f)

def evaluate_review(answer_key: dict, reviewer_output: ReviewOutput) -> dict:
    seeded_flaws = answer_key["seeded_flaws"]
    actual_findings = reviewer_output.findings

    # Tracking variables
    detected = []
    missed = []
    false_flags = []
    severity_matches = 0

    # 1. Check Seeded Flaws (Detection & Calibration)
    for flaw in seeded_flaws:
        match = None
        for finding in actual_findings:
            # We match based on the criterion and the finding_type
            # (In a more complex system, we'd match on evidence quote text too)
            if (finding.criterion == flaw["criterion"] and 
                finding.finding_type == flaw["finding_type"]):
                match = finding
                break
        
        if match:
            detected.append(flaw)
            # Check if the severity matches expected
            if match.severity == flaw["expected_severity"]:
                severity_matches += 1
        else:
            missed.append(flaw)

    # 2. Check for False Flags
    # A false flag is an actual finding that does NOT match any seeded flaw
    for finding in actual_findings:
        is_false_flag = True
        for flaw in seeded_flaws:
            if (finding.criterion == flaw["criterion"] and 
                finding.finding_type == flaw["finding_type"]):
                is_false_flag = False
                break
        if is_false_flag:
            false_flags.append(finding)

    # 3. Calculate Rates
    total_flaws = len(seeded_flaws)
    detection_rate = (len(detected) / total_flaws) * 100 if total_flaws > 0 else 0
    false_flag_rate = (len(false_flags) / len(actual_findings)) * 100 if len(actual_findings) > 0 else 0
    calibration_rate = (severity_matches / len(detected)) * 100 if len(detected) > 0 else 0

    return {
        "metrics": {
            "detection_rate": f"{detection_rate:.1f}%",
            "false_flag_rate": f"{false_flag_rate:.1f}%",
            "severity_calibration": f"{calibration_rate:.1f}%"
        },
        "details": {
            "detected": [f["description"][:50] + "..." for f in detected],
            "missed": [f["description"][:50] + "..." for f in missed],
            "false_flags": [f.issue for f in false_flags]
        }
    }

if __name__ == "__main__":
    # Load our audited answer key
    answer_key = load_json("evals/answer_key.json")

    # Create a FAKE reviewer output to test the scoring engine.
    # This fake output finds 3 things correctly, misses the rest, and invents 1 thing.
    fake_output = ReviewOutput(
        prd_id="seed_01",
        findings=[
            # 1. Caught, correct severity
            Finding(
                criterion="metrics", finding_type="no_baseline", severity="high", severity_source="code_fixed",
                evidence=[{"quote": "improve user satisfaction"}], issue="No baseline."
            ),
            # 2. Caught, correct severity
            Finding(
                criterion="requirements", finding_type="missing_priority", severity="high", severity_source="code_fixed",
                evidence=[{"quote": "Add a toggle in Settings."}], issue="No priority."
            ),
            # 3. Caught, WRONG severity (Expected medium, got low)
            Finding(
                criterion="requirements", finding_type="untestable_ac", severity="low", severity_source="model_provisional",
                evidence=[{"quote": "Ensure the app is fast"}], issue="Untestable."
            ),
            # 4. FALSE FLAG (Invented a problem that wasn't seeded)
            Finding(
                criterion="scope", finding_type="missing_timeline", severity="medium", severity_source="code_fixed",
                evidence=[{"quote": "We will build a dark mode"}], issue="Scope has no dates."
            )
        ]
    )

    results = evaluate_review(answer_key, fake_output)
    
    print("=== EVAL SCORECARD ===")
    print(json.dumps(results, indent=2))