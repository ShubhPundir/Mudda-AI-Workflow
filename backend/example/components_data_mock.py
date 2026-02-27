components_data = [
    {
        "name": "call_plumber_component",
        "description": "Contact the emergency plumber service and schedule repair.",
        "category": "Emergency Services",
        "activities": [
            {"activity_name": "llm_generate_dispatch_text_activity", "description": "Generates clear dispatch instructions for the plumber service.", "retry_policy": {"initial_interval": 5, "maximum_attempts": 3}},
            {"activity_name": "contact_plumber", "description": "Calls the external Plumber Service API to book a technician.", "retry_policy": {"initial_interval": 10, "maximum_attempts": 5}},
            {"activity_name": "human_feedback_activity", "description": "Waits for a dispatcher to confirm the appointment.", "retry_policy": {"initial_interval": 60, "maximum_attempts": 1}}
        ],
        "config": {}
    },
    {
        "name": "plumber_followup_component",
        "description": "Handle the reception of follow-up information from the plumber after dispatch.",
        "category": "Emergency Services",
        "activities": [
            {"activity_name": "await_plumber_confirmation_activity", "description": "Sets a wait-state to receive asynchronous confirmation from the technician.", "retry_policy": {"maximum_attempts": 1}},
            {"activity_name": "human_verification_activity", "description": "Official manually verifies the quality of work reported by the plumber.", "retry_policy": {"maximum_attempts": 2}},
            {"activity_name": "update_issue", "description": "Updates the main issue status to Resolved and attaches logs.", "retry_policy": {"maximum_attempts": 3}}
        ],
        "config": {}
    },
    {
        "name": "civic_issue_analyzer",
        "description": "AI analysis of a civic issue followed by a PDF report generation and S3 upload.",
        "category": "Analytics",
        "activities": [
            {"activity_name": "generate_llm_content", "description": "Analyzes the problem and generates a structured summary.", "retry_policy": {"maximum_attempts": 3}},
            {"activity_name": "pdf_service_activity", "description": "Converts AI summary to PDF and uploads result to the cloud.", "retry_policy": {"maximum_attempts": 3}},
            {"activity_name": "update_issue", "description": "Links the generated report URL to the civic issue record.", "retry_policy": {"maximum_attempts": 2}}
        ],
        "config": {}
    },
    {
        "name": "send_service_email",
        "description": "Generate content and send an email notification to external stakeholders.",
        "category": "Notifications",
        "activities": [
            {"activity_name": "generate_llm_content", "description": "Crafts a professional notification message based on context.", "retry_policy": {"maximum_attempts": 3}},
            {"activity_name": "pdf_service_activity", "description": "Prepares and uploads any necessary attachments.", "retry_policy": {"maximum_attempts": 3}},
            {"activity_name": "send_notification", "description": "Dispatches the email via SendGrid/Resend.", "retry_policy": {"maximum_attempts": 3}}
        ],
        "config": {}
    }
]
