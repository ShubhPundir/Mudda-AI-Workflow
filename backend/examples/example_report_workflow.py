from datetime import timedelta
from typing import Any, Dict
from temporalio import workflow

# Import activities
# In a real setup, we use string names or import the activity definitions
with workflow.unsafe.imports_passed_through():
    from activities.document_activities import generate_report
    from activities.notification_activities import send_notification

@workflow.defn
class ExampleReportWorkflow:
    """
    Workflow that:
    1. Generates a report using AI (Gemini) -> PDF.
    2. Sends the generated PDF as an email attachment.
    """

    @workflow.run
    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Run the report generation and email flow.
        """
        workflow.logger.info("Starting ExampleReportWorkflow for topic: %s", input_data.get("problem_statement"))

        # Step 1: Generate Report (AI + PDF)
        # The generate_report activity internally calls LLMService and PDFGenerator
        report_result = await workflow.execute_activity(
            generate_report,
            input_data,
            start_to_close_timeout=timedelta(minutes=2),
        )

        workflow.logger.info("Report generated at: %s", report_result["file_path"])

        # Step 2: Send Email with Attachment
        email_payload = {
            "to": input_data.get("email_to", "project.mudda@gmail.com"),
            "subject": f"Mudda AI Report: {input_data.get('title', 'Generated Analysis')}",
            "body": f"Please find the attached report regarding: {input_data.get('problem_statement')}",
            "attachments": [
                {
                    "path": report_result["file_path"],
                    "filename": report_result["filename"]
                }
            ],
            "step_id": report_result.get("step_id")
        }

        email_result = await workflow.execute_activity(
            send_notification,
            email_payload,
            start_to_close_timeout=timedelta(minutes=1),
        )

        workflow.logger.info("Report emailed successfully. Message ID: %s", email_result["message_id"])

        return {
            "report": report_result,
            "email": email_result,
            "status": "success"
        }
