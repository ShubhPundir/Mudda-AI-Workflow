"""
Example: Using Structured Output with Gemini and Pydantic

This demonstrates the new structured output approach that replaces
fragile regex-based JSON extraction with hard schema validation.
"""
import asyncio
from typing import List
from pydantic import BaseModel, Field, field_validator
from sessions.llm.llm_factory import LLMFactory


# Define your response schema
class CivicIssueAnalysis(BaseModel):
    """Schema for civic issue analysis"""
    issue_category: str = Field(..., description="Category of the civic issue")
    severity: str = Field(..., description="Severity level: low, medium, high, critical")
    affected_departments: List[str] = Field(..., description="List of affected departments")
    estimated_resolution_days: int = Field(..., ge=1, le=365, description="Days to resolve")
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        valid_levels = {'low', 'medium', 'high', 'critical'}
        if v.lower() not in valid_levels:
            raise ValueError(f"Severity must be one of {valid_levels}")
        return v.lower()


async def analyze_civic_issue_old_way():
    """
    ❌ OLD WAY: Fragile regex-based extraction
    """
    import re
    import json
    
    llm = LLMFactory.get_llm_service()
    
    prompt = """
    Analyze this civic issue: "Pothole on Main Street causing traffic delays"
    
    Respond in JSON format:
    {
        "issue_category": "...",
        "severity": "...",
        "affected_departments": [...],
        "estimated_resolution_days": ...
    }
    """
    
    response = await llm.generate_async(prompt)
    response_text = response.text if hasattr(response, "text") else str(response)
    
    # Fragile regex extraction
    json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', response_text, re.DOTALL)
    if json_match:
        json_str = json_match.group(1)
    else:
        json_match = re.search(r'\{.*\}', response_text, re.DOTALL)
        json_str = json_match.group(0) if json_match else response_text
    
    # Hope it parses correctly!
    data = json.loads(json_str)
    
    # Manual validation
    if "issue_category" not in data:
        raise ValueError("Missing issue_category")
    
    return data


async def analyze_civic_issue_new_way():
    """
    ✅ NEW WAY: Structured output with Pydantic validation
    """
    llm = LLMFactory.get_llm_service()
    
    prompt = """
    Analyze this civic issue: "Pothole on Main Street causing traffic delays"
    
    Provide a structured analysis with:
    - Issue category
    - Severity level (low, medium, high, critical)
    - Affected departments
    - Estimated resolution time in days
    """
    
    # Zero regex, hard schema validation!
    analysis = await llm.generate_structured(
        prompt,
        CivicIssueAnalysis
    )
    
    # Guaranteed to be valid at this point
    return analysis


async def main():
    """Compare old vs new approach"""
    
    print("=" * 60)
    print("STRUCTURED OUTPUT EXAMPLE")
    print("=" * 60)
    
    # New way (recommended)
    print("\n✅ NEW WAY: Structured Output")
    print("-" * 60)
    try:
        result = await analyze_civic_issue_new_way()
        print(f"Category: {result.issue_category}")
        print(f"Severity: {result.severity}")
        print(f"Departments: {', '.join(result.affected_departments)}")
        print(f"Est. Resolution: {result.estimated_resolution_days} days")
        print("\n✓ Type-safe, validated, zero regex!")
    except Exception as e:
        print(f"✗ Error: {e}")
    
    print("\n" + "=" * 60)
    print("KEY BENEFITS")
    print("=" * 60)
    print("""
    1. Zero regex patterns - no fragile text extraction
    2. Hard schema validation at decode time
    3. Type safety with Pydantic
    4. Clear error messages on validation failures
    5. Gemini enforces JSON schema at generation time
    6. Production-ready for civic systems
    """)


if __name__ == "__main__":
    asyncio.run(main())
