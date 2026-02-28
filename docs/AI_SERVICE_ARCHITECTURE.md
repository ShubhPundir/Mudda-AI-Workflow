# AI Service Architecture

## Overview

The AI Service orchestrates workflow generation using Gemini AI and LangGraph. It features:
- **Structured output** with Pydantic validation (zero regex)
- **Modular node architecture** for maintainability
- **Multi-agent workflow** with activity selection and plan generation

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                      AI Service                              │
│  (Orchestration layer - LangGraph workflow)                 │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                   AI Nodes (Modular)                         │
│  ├── activity_selector_node.py                              │
│  ├── plan_maker_node.py                                     │
│  ├── graph_state.py (shared state)                          │
│  └── prompts.py (centralized prompts)                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              LLM Interface (Structured Output)               │
│  generate_structured(prompt, schema) -> BaseModel           │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│              Gemini LLM Adapter                              │
│  • JSON mode with schema enforcement                        │
│  • Pydantic validation                                      │
└─────────────────────┬───────────────────────────────────────┘
                      │
                      ▼
┌─────────────────────────────────────────────────────────────┐
│                 Pydantic Schemas                             │
│  • ActivitySelectionResponse                                │
│  • WorkflowPlanResponse                                     │
│  • Field validators + DAG cycle detection                   │
└─────────────────────────────────────────────────────────────┘
```

## Modular Node Architecture

### File Structure

```
services/
├── ai_service.py                      # Orchestration (120 lines)
└── ai_nodes/
    ├── __init__.py                    # Package exports
    ├── graph_state.py                 # Shared state definition
    ├── prompts.py                     # Centralized prompts
    ├── activity_selector_node.py     # Activity selection logic
    └── plan_maker_node.py            # Plan generation logic
```

### Benefits

- **Separation of concerns** - Each node has single responsibility
- **Testability** - Nodes can be tested independently
- **Reusability** - Nodes can be composed into different workflows
- **Maintainability** - Changes isolated to specific nodes
- **Extensibility** - Easy to add new nodes

### Graph State

Shared state passed between nodes:

```python
class GraphState(TypedDict):
    problem_statement: str
    selected_activity_ids: List[str]
    selected_activities: List[Dict[str, Any]]
    workflow_json: Dict[str, Any]
    error: str
    current_step: str
    message: str
```

### Workflow Flow

```
START
  ↓
activity_selector_node
  ↓ (selects relevant activities)
plan_maker_node
  ↓ (generates workflow plan)
END
```

## Structured Output

### Why Structured Output?

**Problem with regex extraction:**
```python
# ❌ Fragile - breaks on formatting changes
json_match = re.search(r'```json\s*(\{.*?\})', response.text)
data = json.loads(json_match.group(1))  # Hope it works!
```

**Solution with structured output:**
```python
# ✅ Robust - schema enforced at generation time
response = await llm.generate_structured(prompt, MySchema)
# Guaranteed valid, type-safe, zero regex!
```

### Validation Layers

1. **Gemini JSON Schema** - Enforces structure at generation time
2. **JSON Parsing** - Validates JSON syntax
3. **Pydantic Validation** - Validates types and constraints
4. **Domain Validation** - Checks business rules (DAG cycles, ID existence)

### Schemas

**Activity Selection:**
```python
class ActivitySelectionResponse(BaseModel):
    selected_activity_ids: List[str] = Field(..., min_length=1)
```

**Workflow Plan:**
```python
class WorkflowPlanResponse(BaseModel):
    workflow_name: str
    description: str
    steps: List[WorkflowStep]
    
    @field_validator('steps')
    def validate_dag_structure(cls, steps):
        # Automatic cycle detection
        ...
```

## Usage

### Basic Usage

```python
from services.ai_service import ai_service

# Generate workflow plan
result = await ai_service.generate_workflow_plan(
    "Fix pothole on Main Street"
)

print(result["workflow_name"])
print(result["steps"])
```

### Streaming Usage

```python
async for event in ai_service.generate_workflow_plan_stream(problem):
    if event["event"] == "activity_selection_complete":
        print(f"Selected: {event['data']['activities']}")
    elif event["event"] == "workflow_generation_complete":
        print(f"Workflow: {event['data']['workflow']}")
```

### Testing Individual Nodes

```python
from services.ai_nodes import activity_selector_node

state = {
    "problem_statement": "Test problem",
    "selected_activity_ids": [],
    "selected_activities": [],
    "workflow_json": {},
    "error": "",
    "current_step": "",
    "message": ""
}

result = await activity_selector_node(state)
assert result["selected_activity_ids"]
```

## Adding New Nodes

### Step 1: Create Node File

```python
# services/ai_nodes/validator_node.py
from .graph_state import GraphState

async def validator_node(state: GraphState) -> GraphState:
    """Validates workflow before execution"""
    new_state = state.copy()
    
    try:
        # Validation logic
        new_state["current_step"] = "validation_complete"
        return new_state
    except Exception as e:
        new_state["error"] = str(e)
        return new_state
```

### Step 2: Export in `__init__.py`

```python
from .validator_node import validator_node

__all__ = [
    "activity_selector_node",
    "plan_maker_node",
    "validator_node"  # Add new node
]
```

### Step 3: Use in Workflow

```python
# In ai_service.py
from .ai_nodes import validator_node

workflow.add_node("validator", validator_node)
workflow.add_edge("plan_maker", "validator")
workflow.add_edge("validator", END)
```

## Error Handling

### Node-Level Errors

Each node catches exceptions and sets error field:

```python
try:
    # Node logic
    return new_state
except Exception as e:
    new_state["error"] = str(e)
    return new_state
```

### Service-Level Errors

Service checks for errors and raises:

```python
final_state = await self.app.ainvoke(initial_state)

if final_state.get("error"):
    raise ValueError(final_state["error"])
```

### Validation Errors

Pydantic provides detailed error messages:

```
ValidationError: 1 validation error for WorkflowPlanResponse
workflow_name
  Field required [type=missing, input_value={...}]
```

## Best Practices

### 1. State Immutability
```python
new_state = state.copy()  # Always copy
new_state["field"] = "value"
return new_state
```

### 2. Progress Tracking
```python
new_state["current_step"] = "step_name"
new_state["message"] = "Human-readable message"
```

### 3. Error Handling
```python
try:
    # Logic
    return new_state
except Exception as e:
    new_state["error"] = str(e)
    return new_state
```

### 4. Validation
```python
if not state.get("required_field"):
    raise ValueError("Missing required field")
```

## Testing

### Unit Tests

```python
@pytest.mark.asyncio
async def test_activity_selector():
    state = {...}
    result = await activity_selector_node(state)
    assert result["current_step"] == "activity_selection_complete"
```

### Integration Tests

```python
@pytest.mark.asyncio
async def test_full_workflow():
    service = AIService()
    result = await service.generate_workflow_plan("Fix pothole")
    assert "workflow_name" in result
```

## Performance

- **Async/Await** - Non-blocking execution
- **Streaming** - Real-time progress updates
- **Parallel Nodes** - LangGraph supports parallel execution
- **Caching** - Can cache expensive operations

## Production Benefits

For civic systems where **malformed JSON = broken citizen workflow**:

✅ **Reliability** - No silent failures from malformed JSON  
✅ **Debuggability** - Clear error messages  
✅ **Maintainability** - Modular, testable code  
✅ **Type Safety** - Full Pydantic validation  
✅ **Extensibility** - Easy to add new nodes  

## Future Enhancements

Potential additions:
- Validation node for workflow verification
- Optimization node for workflow improvement
- Human-in-the-loop approval node
- Retry logic node for error recovery
- Monitoring node for telemetry

## References

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [Pydantic Documentation](https://docs.pydantic.dev/)
- [Temporal Architecture](./temporal_architecture.md)
