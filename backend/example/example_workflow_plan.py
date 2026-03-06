"""
Example static workflow plan for testing worker dispatch workflow.

This plan:
1. Dispatches a worker (plumber) to a location
2. Requests site photos from the dispatched worker
3. Confirms task completion

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

WORKER_DISPATCH_WORKFLOW_PLAN = {
    "workflow_name": "Worker Dispatch and Site Documentation",
    "description": "Dispatch a worker to a site, request photos, and confirm completion",
    "steps": [
        {
            "step_id": "step_001_dispatch_worker",
            "activity_id": "dispatch_worker_activity",
            "description": "Dispatch a plumber to fix a water pipe burst",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_001_dispatch_worker",
                "worker_type": "plumber",
                "issue_id": "ISSUE-2024-00187",
                "location": "42 MG Road, Sector 14, Gurugram",
                "urgency": "critical",
                "description": "Major water pipe burst causing flooding in the residential area"
            }
        },
        {
            "step_id": "step_002_request_photos",
            "activity_id": "request_site_photos_activity",
            "description": "Request site photos from the dispatched worker",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_002_request_photos",
                "dispatch_id": "{{step_001_dispatch_worker.dispatch_id}}",
                "message": "Please upload high-resolution photos of the broken pipe before starting repairs and after completion."
            }
        },
        {
            "step_id": "step_003_confirm_completion",
            "activity_id": "confirm_task_completion_activity",
            "description": "Confirm the task has been completed",
            "requires_approval": False,
            "inputs": {
                "step_id": "step_003_confirm_completion",
                "dispatch_id": "{{step_001_dispatch_worker.dispatch_id}}",
                "notes": "Worker has uploaded photos and marked the repair as complete. Pipe has been fixed and pressure tested."
            }
        }
    ]
}
