"""
Example static workflow plan for testing document generation and email notification.

This plan:
1. Generates a 300-word PDF document about photosynthesis
2. Sends the document via email to shb.pndr@gmail.com

This mimics what ai_service.py would generate, but with static data for testing.
"""

PHOTOSYNTHESIS_WORKFLOW_PLAN = {
    "workflow_name": "Photosynthesis Document Generation and Email",
    "description": "Generate a PDF about photosynthesis and email it",
    "steps": [
        {
            "step_id": "step_001_generate_pdf",
            "activity_id": "pdf_service_activity",
            "description": "Generate a 300-word PDF document about photosynthesis",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_001_generate_pdf",
                "problem_statement": "Create a comprehensive 300-word educational document explaining the process of photosynthesis, including its importance, the chemical equation, light-dependent and light-independent reactions, and its role in the ecosystem.",
                "title": "Understanding Photosynthesis: Nature's Energy Conversion",
                'report_type': 'educational'
            }
        },
        {
            "step_id": "step_002_send_email",
            "activity_id": "send_notification",
            "description": "Email the generated PDF to shb.pndr@gmail.com",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_002_send_email",
                "to": "shb.pndr@gmail.com",
                "content": "Send an email about the photosynthesis educational document. Mention that a comprehensive educational document about photosynthesis has been generated covering the fundamental process, chemical equations, light-dependent and light-independent reactions, and ecological importance. The document is available for download at {{step_001_generate_pdf.s3_url}}",
                "issue_id": "example_photosynthesis_001"
            }
        }
    ]
}
