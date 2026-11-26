from pydantic import BaseModel, Field
from typing import List, Literal, Optional

class Evidence(BaseModel):
    quote: str
    status: Literal["verified", "partial"] = "verified"

class Finding(BaseModel):
    criterion: Literal["metrics", "requirements", "scope", "clarity"]
    finding_type: str
    severity: Literal["high", "medium", "low"]
    severity_source: Literal["code_fixed", "code_keyed", "code_rubric", "model_provisional"]
    severity_key: Optional[str] = None
    evidence: List[Evidence]
    issue: str
    suggestion: Optional[str] = None
    extensions: dict = Field(default_factory=dict)

class ReviewOutput(BaseModel):
    prd_id: str
    findings: List[Finding]