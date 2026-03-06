# Temporal Workflow Architecture

## Overview

This document explains how the Temporal workflow system works in the Mudda AI Workflow application. The system is split into three core components that work together to execute civic issue resolution workflows in a reliable, distributed manner.

## Core Components

### 1. Temporal Client (`backend/temporal/client.py`)

The client is responsible for **initiating and controlling workflows** from your FastAPI application.

**Key Responsibilities:**
- Connects to the Temporal server
- Starts workflow executions
- Sends signals to running workflows (e.g., approval notifications)
- Queries workflow status
- Retrieves workflow results

**Connection Management:**
```python
# Connects to Temporal server (idempotent)
host = os.getenv("TEMPORAL_HOST", "localhost:7233")
namespace = os.getenv("TEMPORAL_NAMESPACE", "default")
```

**Main Operations:**

1. **execute_workflow()** - Starts a new workflow execution
   - Takes a workflow plan (dict with steps) and execution ID
   - Returns a Temporal workflow ID for tracking
   - Uses task queue: `mudda-ai-workflows`

2. **signal_approval()** - Sends approval signal to waiting workflows
   - Used for human-in-the-loop steps
   - Non-blocking operation

3. **get_workflow_result()** - Waits for workflow completion
   - Blocking call that returns final results
   - Used to retrieve execution outcomes

4. **query_workflow_status()** - Gets current workflow state
   - Non-blocking query
   - Returns execution_results, ai_context, approved_steps

**Singleton Pattern:**
```python
temporal_client_manager = TemporalClientManager()
```
A global instance is exported for use across the application.

---

### 2. Temporal Worker (`backend/temporal/worker.py`)

The worker is a **separate process** that executes workflow and activity code.

**Key Responsibilities:**
- Connects to Temporal server
- Registers workflow classes
- Registers activity functions
- Polls for tasks from the task queue
- Executes workflows and activities

**Registration Pattern:**
```python
# Workflows: registered as classes
workflows=[MuddaWorkflow]

# Activities: registered as individual functions (NOT classes)
all_activities = [
    getattr(activities, name) 
    for name in activities.__all__
]
```

**Important:** Activities must be registered as callable functions, not class instances. This is the correct pattern for temporalio-python.

**Lifecycle:**
1. `_connect()` - Establishes connection to Temporal server
2. `_create_worker()` - Creates worker with registered workflows/activities
3. `start()` - Begins polling and executing tasks (blocking)
4. `shutdown()` - Gracefully stops the worker

**Deployment:**
- Runs as a standalone process (separate from FastAPI)
- Can be scaled horizontally (multiple workers)
- All workers share the same task queue

---

### 3. MuddaWorkflow (`backend/workflows/mudda_workflow.py`)

The workflow orchestrates the execution of a multi-step civic issue resolution plan.

**Determinism Rules (Critical):**

Temporal workflows must be deterministic for replay reliability:
- ❌ NO database calls
- ❌ NO `datetime.now()` / `random` / `uuid`
- ❌ NO external API or AI calls
- ✅ ALL side-effects through activities
- ✅ Human approval via Temporal signals

**Workflow State:**
```python
self.execution_results: Dict[str, Any] = {}  # Results from each step
self.ai_context: Dict[str, Any] = {}         # AI metadata
self.approved_steps: Dict[str, bool] = {}    # Approval tracking
```

**Main Components:**

1. **Signals** - Receive external events
   ```python
   @workflow.signal
   def approve_step(self, step_id: str) -> None:
       self.approved_steps[step_id] = True
   ```

2. **Queries** - Read workflow state (non-blocking)
   ```python
   @workflow.query
   def get_status(self) -> Dict[str, Any]:
       return {"execution_results": ..., "ai_context": ..., ...}
   ```

3. **Run Method** - Main execution logic
   ```python
   @workflow.run
   async def run(self, workflow_plan: Dict[str, Any], execution_id: str):
       # Execute steps sequentially
   ```

**Execution Flow:**

1. Mark execution as "running" (via activity)
2. For each step in the plan:
   - Check if approval required → wait for signal
   - Resolve template variables in inputs
   - Execute activity with retry policy
   - Store results in workflow state
   - Update ai_context if relevant
3. Mark execution as "completed" or "failed"
4. Return final results

**Template Resolution:**

Supports variable substitution in activity inputs:
```python
# Example: {{step_1.document_url}}
# Resolves to: self.execution_results["step_1"]["document_url"]
```

**Error Handling:**
- Activities have retry policy (3 attempts, exponential backoff)
- Step failures are caught and recorded
- Partial results are preserved
- Execution status updated to "failed" in database

---

## How They Work Together

### Workflow Execution Sequence

```
1. FastAPI receives request to execute workflow plan
   ↓
2. temporal_client_manager.execute_workflow(plan, exec_id)
   ↓
3. Temporal server receives workflow start request
   ↓
4. Worker polls task queue and picks up workflow task
   ↓
5. Worker executes MuddaWorkflow.run()
   ↓
6. Workflow executes activities sequentially
   ↓
7. Each activity is executed by worker (with retries)
   ↓
8. If step requires approval:
   - Workflow waits for signal
   - Client sends signal via signal_approval()
   - Workflow continues
   ↓
9. Workflow completes and returns results
   ↓
10. Client retrieves results via get_workflow_result()
```

### Human-in-the-Loop Pattern

```
Workflow: await workflow.wait_condition(
    lambda: self.approved_steps.get(step_id, False)
)
                    ↓
            [Workflow pauses]
                    ↓
User approves via API → Client.signal_approval(workflow_id, step_id)
                    ↓
            [Workflow resumes]
```

### Activity Execution Pattern

```
Workflow: await workflow.execute_activity(
    activity_handler,
    args=[inputs],
    start_to_close_timeout=timedelta(minutes=5),
    retry_policy=retry
)
                    ↓
Worker executes activity function (e.g., generate_document)
                    ↓
Activity performs side-effects (DB, API, AI calls)
                    ↓
Returns result to workflow
                    ↓
Workflow stores result in self.execution_results
```

---

## Key Design Patterns

### 1. Separation of Concerns
- **Client**: Workflow control (start, signal, query)
- **Worker**: Workflow/activity execution
- **Workflow**: Orchestration logic (deterministic)
- **Activities**: Side-effects (non-deterministic)

### 2. Retry & Reliability
- Activities have automatic retry with exponential backoff
- Workflows are durable (survive process crashes)
- State is persisted by Temporal server

### 3. Observability
- Structured logging at each step
- Query support for real-time status
- Execution results tracked in workflow state

### 4. Scalability
- Workers can be scaled horizontally
- Task queue distributes work across workers
- Client and worker run in separate processes

---

## Configuration

**Environment Variables:**
```bash
TEMPORAL_HOST=localhost:7233        # Temporal server address
TEMPORAL_NAMESPACE=default          # Temporal namespace
```

**Task Queue:**
```python
TASK_QUEUE = "mudda-ai-workflows"   # Shared across client and worker
```

---

## Deployment Architecture

```
┌─────────────────┐
│  FastAPI App    │
│  (Client)       │
└────────┬────────┘
         │ gRPC
         ↓
┌─────────────────┐
│ Temporal Server │
│  (Orchestrator) │
└────────┬────────┘
         │ Task Queue
         ↓
┌─────────────────┐
│ Worker Process  │
│ (Executor)      │
└─────────────────┘
```

**Process Separation:**
- FastAPI runs the client (starts workflows)
- Separate worker process executes workflows
- Both connect to the same Temporal server
- Database accessed only through activities

---

## Best Practices

1. **Never call database directly from workflow code**
   - Use activities for all DB operations

2. **Keep workflows deterministic**
   - No random values, timestamps, or external calls
   - Use activities for non-deterministic operations

3. **Use signals for human approval**
   - Don't use activity sleep loops
   - Signals are the correct pattern

4. **Store context in workflow state**
   - Results, AI metadata, approval status
   - Queryable from outside

5. **Handle failures gracefully**
   - Retry policies on activities
   - Partial results preserved
   - Clear error messages

---

## Summary

The Temporal architecture provides a robust, scalable foundation for executing complex, long-running workflows with human-in-the-loop steps. The separation between client, worker, and workflow ensures reliability, while the activity pattern enables safe side-effects with automatic retries.
