import os
import re
from typing import List
from openai import OpenAI  
from prd_reviewer.schema import Finding, Evidence
from prd_reviewer.metrics import extract_section
from dotenv import load_dotenv  

load_dotenv()  # <-- ADD THIS

client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

def check_scope(prd_text: str) -> List[Finding]:
    # ... the rest of the code
    findings = []

    # --- PART 1: CODE CHECKS ---
    scope_text = extract_section(prd_text, ["Scope"])
    non_goals_text = extract_section(prd_text, ["Non-Goals", "Non Goals", "Out of Scope"])

    if not scope_text:
        findings.append(Finding(
            criterion="scope",
            finding_type="missing_scope",
            severity="high",
            severity_source="code_fixed",
            evidence=[Evidence(quote="No Scope section found")],
            issue="The PRD does not have a Scope section.",
            suggestion="Add a section defining what is in scope."
        ))
    
    if not non_goals_text:
        findings.append(Finding(
            criterion="scope",
            finding_type="missing_non_goals",
            severity="medium",
            severity_source="code_fixed",
            evidence=[Evidence(quote="No Non-Goals section found")],
            issue="The PRD does not have a Non-Goals section.",
            suggestion="Add a section explicitly stating what is out of scope."
        ))
        # If there are no non-goals, we can't check if they are vacuous.
        return findings

    # --- PART 2: MODEL CHECK (Vacuous Non-Goals) ---
    # This uses the declared rubric pattern: the model classifies, code assigns severity.
    
    client = OpenAI(
    api_key=os.environ.get("GROQ_API_KEY"),
    base_url="https://api.groq.com/openai/v1",
)

    prompt = f"""
    You are a senior Product Manager. Review the following Non-Goals section from a PRD.
    Are these non-goals meaningful (do they actually exclude real features/work), or are they vacuous (e.g., "we won't build bad things", "we won't crash")?
    
    Non-Goals section:
    {non_goals_text}
    
    Return a JSON object exactly like this:
    {{
        "is_vacuous": true, 
        "evidence_quote": "the exact text from the non-goals that proves your point"
    }}
    Do not include any other text. Just the JSON.
    """
    
    try:
        response = client.chat.completions.create(
            model="openai/gpt-oss-20b",
            messages=[
                {"role": "system", "content": "You are a senior Product Manager. Return only JSON."},
                {"role": "user", "content": prompt}
            ],
            temperature=0,
        )
        
        # Extract JSON from the response
        raw_text = response.choices[0].message.content.strip()
        # Sometimes the model wraps it in ```json ... ```
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:-3].strip()
        
        import json
        result = json.loads(raw_text)
        
        if result.get("is_vacuous"):
            findings.append(Finding(
                criterion="scope",
                finding_type="vacuous_non_goals",
                severity="medium", # Declared rubric: vacuous = medium
                severity_source="code_rubric",
                severity_key="vacuous_non_goals",
                evidence=[Evidence(quote=result.get("evidence_quote", non_goals_text))],
                issue="The non-goals are vacuous (they don't exclude anything real).",
                suggestion="Replace them with specific features or approaches that are deliberately being excluded."
            ))
            
    except Exception as e:
        print(f"Warning: Model call failed for scope check: {e}")

    return findings