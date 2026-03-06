"""
Issue update activities.

Handles database updates related to civic issue tracking.
Uses async DB sessions safely.
LLM-powered for intelligent data extraction and forwarding.
"""
import logging
from temporalio import activity
from sessions.llm import LLMFactory
from services.issue_service import fetch_issue_details, update_issue
from schemas.activity_schemas import (
    UpdateIssueInput,
    UpdateIssueOutput,
    FetchIssueDetailsInput,
    FetchIssueDetailsOutput,
)

logger = logging.getLogger(__name__)
_llm_service = LLMFactory.get_llm_service()


@activity.defn
async def update_issue_activity(input: UpdateIssueInput) -> UpdateIssueOutput:
    """
    Update a civic issue record's status in the database with LLM-enhanced status summary.

    Args:
        input: UpdateIssueInput containing issue_id, status, and step_id.

    Returns:
        UpdateIssueOutput confirming the update with intelligent data for next steps.
    """
    logger.info(
        "update_issue_activity — step_id=%s issue_id=%s",
        input.step_id,
        input.issue_id,
    )

    try:
        # Generate intelligent status summary using LLM
        # prompt = f"Generate a concise status update summary for issue {input.issue_id} with new status: {input.status}"
        # logger.info("Generating LLM-enhanced status summary")
        # status_summary = await _llm_service.generate_report({"problem_statement": prompt})
        
        # Call service to perform update
        result = await update_issue(input.issue_id, input.status)
        

        # TODO: commenting LLM enhancement, all of this must be given to the logging system, not to the issue table
        # TODO: make 1. LLM append only logging --> messages, sources (from and to), issue_id, track flow, 
        # TODO: make 2. make 
        # Enhance result with LLM-generated summary for downstream activities
        # enhanced_result = result.copy() if isinstance(result, dict) else {"raw_result": result}
        # enhanced_result["llm_summary"] = status_summary
        # enhanced_result["next_step_recommendation"] = f"Issue {input.issue_id} updated to {input.status}"
        
        return UpdateIssueOutput(
            step_id=input.step_id,
            issue_id=input.issue_id,
            status="completed"
            # service_result=enhanced_result
        )
    except Exception as exc:
        logger.error("Failed to update issue: %s", exc, exc_info=True)
        raise


# NOTE: keeping it now for backward's compatibility
@activity.defn
async def fetch_issue_details_activity(input: FetchIssueDetailsInput) -> FetchIssueDetailsOutput:
    """
    Fetch details for a specific issue from the API with LLM-powered analysis.

    Args:
        input: FetchIssueDetailsInput containing issue_id and step_id.

    Returns:
        FetchIssueDetailsOutput with issue details and intelligent analysis for next activities.
    """
    logger.info(
        "fetch_issue_details_activity — step_id=%s issue_id=%s",
        input.step_id,
        input.issue_id,
    )

    try:
        details = await fetch_issue_details(input.issue_id)
        
        # Use LLM to analyze issue details and prepare data for downstream activities
        prompt = f"Analyze this issue and extract key information for workflow processing: {details}"
        logger.info("Generating LLM-powered issue analysis")
        analysis = await _llm_service.generate_report({"problem_statement": prompt})
        
        # Enhance details with LLM analysis
        enhanced_details = details.copy() if isinstance(details, dict) else {"raw_details": details}
        enhanced_details["llm_analysis"] = analysis
        enhanced_details["extracted_urgency"] = "medium"  # LLM could extract this
        enhanced_details["recommended_actions"] = analysis

        return FetchIssueDetailsOutput(
            step_id=input.step_id,
            issue_id=input.issue_id,
            status="completed",
            details=enhanced_details
        )
    except Exception as exc:
        logger.error("Failed to fetch issue details: %s", exc, exc_info=True)
        raise
