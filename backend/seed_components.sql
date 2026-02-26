-- Insert Specific Components

INSERT INTO workflow.components (name, description, category, activities)
VALUES 
(
    'call_plumber_component', 
    'Contact the emergency plumber service and schedule repair.', 
    'Emergency Services',
    '[
        {"activity_name": "llm_generate_dispatch_text_activity", "retry_policy": {"initial_interval": 5, "maximum_attempts": 3}},
        {"activity_name": "plumber_dispatch_activity", "retry_policy": {"initial_interval": 10, "maximum_attempts": 5}},
        {"activity_name": "human_feedback_activity", "retry_policy": {"initial_interval": 60, "maximum_attempts": 1}}
    ]'::jsonb
),
(
    'plumber_followup_component', 
    'Handle the reception of follow-up information from the plumber after dispatch. Designed for long-delayed responses using Temporal signals.', 
    'Emergency Services',
    '[
        {
            "activity_name": "await_plumber_confirmation_activity", 
            "purpose": "Initial fast call to notify system that a follow-up is expected.",
            "retry_policy": {"maximum_attempts": 1}
        },
        {
            "activity_name": "human_verification_activity", 
            "purpose": "Allow government official to review plumber response after it arrives.",
            "retry_policy": {"maximum_attempts": 2}
        },
        {
            "activity_name": "update_issue_completion_activity", 
            "purpose": "Update internal issue record with plumber feedback/results.",
            "retry_policy": {"maximum_attempts": 3}
        }
    ]'::jsonb
),
(
    'send_service_email', 
    'Produce a PDF report for internal records and compliance.', 
    'Notifications',
    '[
        {"activity_name": "generate_llm_content", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "pdf_service_activity", "retry_policy": {"maximum_attempts": 3}},
        {"activity_name": "send_email_activity", "retry_policy": {"maximum_attempts": 3}}
    ]'::jsonb
);
