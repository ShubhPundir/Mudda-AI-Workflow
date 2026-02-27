-- Insert Specific Components

INSERT INTO workflow.components (name, description, category, activities)
VALUES 
(
    'call_plumber_component', 
    'Contact the emergency plumber service and schedule repair.', 
    'Emergency Services',
    '[
        {"activity_name": "llm_generate_dispatch_text_activity", "retry_policy": {"initial_interval": 5, "maximum_attempts": 3}},
        {"activity_name": "contact_plumber", "retry_policy": {"initial_interval": 10, "maximum_attempts": 5}},
        {"activity_name": "human_feedback_activity", "retry_policy": {"initial_interval": 60, "maximum_attempts": 1}}
    ]'::jsonb
),
(
    'plumber_followup_component', 
    'Handle the reception of follow-up information from the plumber after dispatch.', 
    'Emergency Services',
    '[
        {
            "activity_name": "await_plumber_confirmation_activity", 
            "retry_policy": {"maximum_attempts": 1}
        },
        {
            "activity_name": "human_verification_activity", 
            "retry_policy": {"maximum_attempts": 2}
        },
        {
            "activity_name": "update_issue", 
            "retry_policy": {"maximum_attempts": 3}
        }
    ]'::jsonb
),
(
    'civic_issue_analyzer', 
    'AI analysis of a civic issue followed by a PDF report generation and S3 upload.', 
    'Analytics',
    '[
        {"activity_name": "generate_llm_content", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "pdf_service_activity", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "update_issue", "retry_policy": {"maximum_attempts": 2}}
    ]'::jsonb
),
(
    'send_service_email', 
    'Generate content and send an email notification to external stakeholders.', 
    'Notifications',
    '[
        {"activity_name": "generate_llm_content", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "pdf_service_activity", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "send_notification", "retry_policy": {"maximum_attempts": 3}}
    ]'::jsonb
);
