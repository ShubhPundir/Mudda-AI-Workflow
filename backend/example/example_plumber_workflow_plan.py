"""
Example static workflow plan for the plumber dispatch demo.

This plan:
1. Opens a bi-directional chat session with the plumber service
2. Generates a PDF field report summarising the completed repair
3. Sends the report via email to the municipal official

This mimics what ai_service.py would generate, but with static data for demo purposes.
"""

PLUMBER_WORKFLOW_PLAN = {
    "workflow_name": "Emergency Plumber Dispatch and Reporting",
    "description": "Dispatch a plumber via bi-directional chat, generate a field report, and email it to the official",
    "steps": [
        {
            "step_id": "step_001_contact_plumber",
            "activity_id": "contact_plumber",
            "description": "Open a bi-directional chat session with the plumber service for a burst pipe emergency",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_001_contact_plumber",
                "issue_id": "ISSUE-2024-00187",
                "location": "42 MG Road, Sector 14, Gurugram, Haryana 122001",
                "description": "Major water pipe burst in the basement parking area causing flooding and water damage to vehicles. Immediate intervention required.",
                "urgency": "critical"
            }
        },
        {
            "step_id": "step_002_generate_report",
            "activity_id": "pdf_service_activity",
            "description": "Generate a field report summarising the plumber chat session and repairs",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_002_generate_report",
                "problem_statement": "Generate a detailed field report for civic issue ISSUE-2024-00187: A major water pipe burst was reported at 42 MG Road, Sector 14, Gurugram. The plumber was dispatched on an emergency basis via a live chat session, arrived on site, and carried out repairs. Include sections on: problem description, actions taken, materials used, resolution status, and follow-up recommendations.",
                "title": "Field Report: Emergency Pipe Burst Repair — 42 MG Road",
                "report_type": "field_report"
            }
        },
        {
            "step_id": "step_003_send_notification",
            "activity_id": "send_notification",
            "description": "Email the field report to the municipal official",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_003_send_notification",
                "to": "shb.pndr@gmail.com",
                "subject": "Field Report: Emergency Pipe Burst Repair — ISSUE-2024-00187",
                "from_name": "Mudda AI Workflow System",
                "issue_id": "ISSUE-2024-00187"
            }
        }
    ]
}
