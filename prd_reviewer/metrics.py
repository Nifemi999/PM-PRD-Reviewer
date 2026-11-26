import re
from typing import List
from prd_reviewer.schema import Finding, Evidence

def extract_section(markdown_text: str, section_names: List[str]) -> str:
    """
    A simple markdown parser. It finds a section by its header name (e.g. "Goals" or "Metrics")
    and returns all text until the next header.
    """
    # Look for #, ##, or ### followed by the section name
    pattern = re.compile(rf"^#+\s*({'|'.join(section_names)})\s*$(.*?)(?=^#+\s|\Z)", re.IGNORECASE | re.MULTILINE | re.DOTALL)
    match = pattern.search(markdown_text)
    if match:
        return match.group(2).strip()
    return ""

def check_metrics(prd_text: str) -> List[Finding]:
    findings = []
    
    # 1. Extract the section
    metrics_text = extract_section(prd_text, ["Goals", "Metrics", "Success Metrics"])
    
    # 2. Code check: Is the section missing or empty?
    if not metrics_text:
        findings.append(Finding(
            criterion="metrics",
            finding_type="missing_section",
            severity="high",
            severity_source="code_fixed",
            evidence=[Evidence(quote="No goals or metrics section found")],
            issue="The PRD does not have a Goals or Metrics section.",
            suggestion="Add a section defining what success looks like."
        ))
        return findings

    # 3. Code check: Does it have a number? (Regex for digits, percentages, currency)
    # We look through all lines in the metrics section
    has_number = False
    has_timeframe = False
    has_baseline = False
    
    for line in metrics_text.split('\n'):
        if not line.strip(): continue
        
        # Check for numbers (e.g., 20, 20%, $500, 1.5x)
        if re.search(r'\d', line):
            has_number = True
            
        # Check for timeframes (e.g., by Q3, within 30 days, by 2024)
        if re.search(r'(by|within|in)\s+(q[1-4]|\d+|jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec|\d{4})', line, re.IGNORECASE):
            has_timeframe = True
            
        # Check for baselines (e.g., from 10%, current is 5, baseline)
        if re.search(r'(from|current|baseline|today)', line, re.IGNORECASE):
            has_baseline = True

    # 4. Generate findings based on what's missing
    # We use the first line of the metrics text as the evidence quote for simplicity
    first_line_quote = metrics_text.split('\n')[0].strip()
    
    if not has_number:
        findings.append(Finding(
            criterion="metrics",
            finding_type="no_number",
            severity="high",
            severity_source="code_fixed",
            evidence=[Evidence(quote=first_line_quote)],
            issue="The metrics section contains no quantitative numbers.",
            suggestion="Add specific numbers or percentages to define the target."
        ))

    if not has_timeframe:
        findings.append(Finding(
            criterion="metrics",
            finding_type="no_timeframe",
            severity="high",
            severity_source="code_fixed",
            evidence=[Evidence(quote=first_line_quote)],
            issue="The metrics section contains no timeframe or deadline.",
            suggestion="Add a date or timeframe (e.g., 'by Q3' or 'within 30 days')."
        ))

    if not has_baseline:
        findings.append(Finding(
            criterion="metrics",
            finding_type="no_baseline",
            severity="high",
            severity_source="code_fixed",
            evidence=[Evidence(quote=first_line_quote)],
            issue="The metrics section does not state the current baseline.",
            suggestion="State the current value before the change (e.g., 'from 10%')."
        ))

    return findings