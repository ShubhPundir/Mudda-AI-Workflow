# Example Workflow Architecture

## System Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                     Example Workflow System                      │
└─────────────────────────────────────────────────────────────────┘

┌──────────────────┐         ┌──────────────────┐
│   Terminal 1     │         │   Terminal 2     │
│                  │         │                  │
│  example_worker  │         │ run_example_     │
│      .py         │         │  workflow.py     │
└────────┬─────────┘         └────────┬─────────┘
         │                            │
         │ Registers                  │ Starts
         │ Activities                 │ Workflow
         │                            │
         ▼                            ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Temporal Server (localhost:7233)              │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              MuddaWorkflow Execution                     │   │
│  │                                                           │   │
│  │  Step 1: pdf_service_activity                           │   │
│  │    ├─ Call LLM to generate text                         │   │
│  │    ├─ Generate PDF                                       │   │
│  │    └─ Upload to S3                                       │   │
│  │                                                           │   │
│  │  Step 2: send_notification                              │   │
│  │    ├─ Resolve template: {{step_001_generate_pdf.s3_url}}│   │
│  │    └─ Send email via provider                           │   │
│  └─────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────┘
         │                            │
         │ Activity                   │ Results
         │ Execution                  │
         ▼                            ▼
┌──────────────────┐         ┌──────────────────┐
│   Activities     │         │    Database      │
│                  │         │                  │
│ • pdf_service    │         │ workflow_        │
│ • send_          │         │  executions      │
│   notification   │         │                  │
└────────┬─────────┘         └──────────────────┘
         │
         │ Calls
         ▼
┌─────────────────────────────────────────────────────────────────┐
│                    External Services                             │
│                                                                   │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐       │
│  │   LLM    │  │   PDF    │  │    S3    │  │  Email   │       │
│  │ (Gemini/ │  │ Generator│  │  Bucket  │  │ Provider │       │
│  │ Bedrock) │  │  (FPDF)  │  │          │  │ (Resend) │       │
│  └──────────┘  └──────────┘  └──────────┘  └──────────┘       │
└─────────────────────────────────────────────────────────────────┘
```

## Component Interaction Flow

### 1. Initialization Phase

```
run_example_workflow.py
    │
    ├─► Create WorkflowExecution record in database
    │   (status: "pending")
    │
    ├─► Connect to Temporal via TemporalClientManager
    │
    └─► Start workflow execution
        └─► Temporal assigns to worker
```

### 2. Worker Registration

```
example_worker.py
    │
    ├─► Connect to Temporal server
    │
    ├─► Register MuddaWorkflow class
    │
    └─► Register all activities:
        ├─► pdf_service_activity
        ├─► send_notification
        ├─► update_execution_status
        └─► ... (all from registry)
```

### 3. Workflow Execution

```
MuddaWorkflow.run()
    │
    ├─► Update execution status to "running"
    │
    ├─► Step 1: Generate PDF
    │   │
    │   └─► Execute pdf_service_activity
    │       │
    │       ├─► LLM generates 300-word text about photosynthesis
    │       ├─► PDF generator creates PDF file
    │       ├─► S3 service uploads PDF
    │       └─► Return: {file_path, s3_url, filename, size_bytes, ai_metadata}
    │
    ├─► Store step 1 results in workflow state
    │
    ├─► Step 2: Send Email
    │   │
    │   └─► Execute send_notification
    │       │
    │       ├─► Resolve template: {{step_001_generate_pdf.s3_url}}
    │       ├─► Email adapter sends email
    │       └─► Return: {message_id, to, subject, status}
    │
    ├─► Store step 2 results in workflow state
    │
    └─► Update execution status to "completed"
```

## Data Flow

### Workflow Plan → Execution

```
example_workflow_plan.py
    │
    │ PHOTOSYNTHESIS_WORKFLOW_PLAN = {
    │   "workflow_name": "...",
    │   "steps": [
    │     {
    │       "step_id": "step_001_generate_pdf",
    │       "activity_id": "pdf_service_activity",
    │       "inputs": {...}
    │     },
    │     {
    │       "step_id": "step_002_send_email",
    │       "activity_id": "send_notification",
    │       "inputs": {
    │         "body": "... {{step_001_generate_pdf.s3_url}} ..."
    │       }
    │     }
    │   ]
    │ }
    ▼
run_example_workflow.py
    │
    └─► temporal_client_manager.execute_workflow(
          workflow_plan=PHOTOSYNTHESIS_WORKFLOW_PLAN,
          execution_id="1"
        )
```

### Template Resolution

```
Step 1 Output:
{
  "step_id": "step_001_generate_pdf",
  "s3_url": "https://s3.amazonaws.com/bucket/report.pdf",
  "file_path": "/tmp/report.pdf",
  ...
}
    │
    │ Stored in: workflow.execution_results["step_001_generate_pdf"]
    │
    ▼
Step 2 Input (before resolution):
{
  "body": "Document available at: {{step_001_generate_pdf.s3_url}}"
}
    │
    │ MuddaWorkflow._resolve_templates()
    │
    ▼
Step 2 Input (after resolution):
{
  "body": "Document available at: https://s3.amazonaws.com/bucket/report.pdf"
}
```

## Activity Execution Pattern

```
┌─────────────────────────────────────────────────────────────┐
│                    Activity Execution                        │
└─────────────────────────────────────────────────────────────┘

Workflow (Deterministic)
    │
    │ workflow.execute_activity(
    │   activity_handler,
    │   args=[inputs],
    │   timeout=5min,
    │   retry_policy=...
    │ )
    │
    ▼
Temporal Server
    │
    │ Routes to worker
    │
    ▼
Worker Process
    │
    │ @activity.defn
    │ async def pdf_service_activity(input):
    │     # Non-deterministic operations allowed here
    │     llm_result = await llm_service.generate(...)
    │     pdf_result = await pdf_service.generate(...)
    │     s3_url = await s3_service.upload(...)
    │     return result
    │
    ▼
External Services
    │
    ├─► LLM API (Gemini/Bedrock)
    ├─► PDF Generator (FPDF)
    ├─► S3 Upload
    └─► Email Provider (Resend/Brevo/etc)
```

## State Management

```
┌─────────────────────────────────────────────────────────────┐
│              MuddaWorkflow State (In-Memory)                 │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  execution_results = {                                       │
│    "step_001_generate_pdf": {                               │
│      "file_path": "/tmp/report.pdf",                        │
│      "s3_url": "https://...",                               │
│      "size_bytes": 15234,                                   │
│      ...                                                     │
│    },                                                        │
│    "step_002_send_email": {                                 │
│      "message_id": "abc123",                                │
│      "to": ["shb.pndr@gmail.com"],                          │
│      ...                                                     │
│    }                                                         │
│  }                                                           │
│                                                               │
│  ai_context = {                                              │
│    "step_001_generate_pdf": {                               │
│      "report_type": "educational",                          │
│      "model": "gemini"                                      │
│    }                                                         │
│  }                                                           │
│                                                               │
│  approved_steps = {}  # Empty (no approval required)        │
│                                                               │
└─────────────────────────────────────────────────────────────┘
         │
         │ Persisted by Temporal
         │
         ▼
┌─────────────────────────────────────────────────────────────┐
│              Temporal Event History                          │
├─────────────────────────────────────────────────────────────┤
│  • WorkflowExecutionStarted                                  │
│  • ActivityTaskScheduled (update_execution_status)          │
│  • ActivityTaskCompleted                                     │
│  • ActivityTaskScheduled (pdf_service_activity)             │
│  • ActivityTaskCompleted                                     │
│  • ActivityTaskScheduled (send_notification)                │
│  • ActivityTaskCompleted                                     │
│  • ActivityTaskScheduled (update_execution_status)          │
│  • ActivityTaskCompleted                                     │
│  • WorkflowExecutionCompleted                               │
└─────────────────────────────────────────────────────────────┘
```

## Error Handling & Retries

```
Activity Execution
    │
    ├─► Success → Return result
    │
    └─► Failure
        │
        ├─► Retry Policy:
        │   • Maximum attempts: 3
        │   • Initial interval: 1s
        │   • Maximum interval: 30s
        │   • Backoff coefficient: 2.0
        │
        ├─► Attempt 1 fails → Wait 1s → Retry
        ├─► Attempt 2 fails → Wait 2s → Retry
        ├─► Attempt 3 fails → Wait 4s → Retry
        │
        └─► All retries exhausted
            │
            └─► Workflow catches exception
                │
                ├─► Update execution status to "failed"
                ├─► Store partial results
                └─► Return failure response
```

## Monitoring Points

```
┌─────────────────────────────────────────────────────────────┐
│                    Monitoring & Observability                │
└─────────────────────────────────────────────────────────────┘

1. Worker Logs (Terminal 1)
   ├─► Activity execution start/end
   ├─► Activity parameters
   └─► Activity results

2. Executor Logs (Terminal 2)
   ├─► Workflow start
   ├─► Workflow progress
   └─► Final results

3. Temporal UI (http://localhost:8233)
   ├─► Workflow timeline
   ├─► Activity execution history
   ├─► Input/output payloads
   └─► Event history

4. Database (workflow_executions table)
   ├─► Execution status
   ├─► Result data
   └─► Timestamps

5. External Service Logs
   ├─► LLM API calls
   ├─► Email delivery status
   └─► S3 upload confirmations
```

## Production vs Example

```
┌─────────────────────────────────────────────────────────────┐
│                    Production System                         │
└─────────────────────────────────────────────────────────────┘

FastAPI Endpoint
    │
    ├─► ai_service.py generates workflow plan
    │   (using LLM to analyze issue and select activities)
    │
    └─► temporal_client_manager.execute_workflow(
          workflow_plan=generated_plan,
          execution_id=...
        )

┌─────────────────────────────────────────────────────────────┐
│                    Example System                            │
└─────────────────────────────────────────────────────────────┘

run_example_workflow.py
    │
    ├─► example_workflow_plan.py (static plan)
    │   (manually created to mimic AI-generated plan)
    │
    └─► temporal_client_manager.execute_workflow(
          workflow_plan=PHOTOSYNTHESIS_WORKFLOW_PLAN,
          execution_id=...
        )

Everything else is IDENTICAL!
```

## Key Architectural Principles

1. **Determinism**: Workflow code is deterministic (no random, datetime.now(), or external calls)
2. **Activity Isolation**: All side effects happen in activities
3. **State Persistence**: Temporal persists workflow state automatically
4. **Retry Logic**: Activities have configurable retry policies
5. **Template Resolution**: Workflow resolves template variables from previous step results
6. **Type Safety**: Pydantic schemas validate all inputs/outputs
7. **Observability**: Comprehensive logging at all levels
8. **Separation of Concerns**: Clear boundaries between workflow, activities, and services
