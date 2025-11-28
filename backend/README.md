# Mudda AI Workflow System

An AI-powered workflow generation system for resolving civic issues using Gemini AI, Temporal.io, PostgreSQL, and REST-based microservices.

## Overview

The Mudda AI Plan Maker is an expert government management officer and workflow automation designer that creates executable workflow plans for civic issues. It uses AI to analyze problem statements and generate structured workflows that can be orchestrated by Temporal.io.

## Features

- 🤖 **AI-Powered Workflow Generation**: Uses Gemini AI to create intelligent workflow plans
- 🔄 **Temporal.io Integration**: Executes workflows with proper orchestration
- 🗄️ **PostgreSQL Database**: Stores components and workflow plans
- 🌐 **REST API**: FastAPI-based endpoints for workflow management
- 📊 **Component Management**: Manage available API components
- ✅ **Human Approval**: Built-in approval workflows for sensitive operations

## Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   FastAPI       │    │   Temporal.io    │    │   PostgreSQL    │
│   REST API      │◄──►│   Workflows     │◄──►│   Database      │
└─────────────────┘    └─────────────────┘    └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐    ┌─────────────────┐
│   Gemini AI     │    │   Microservices │
│   Plan Maker    │    │   (Components)  │
└─────────────────┘    └─────────────────┘
```

## Installation

### Prerequisites

- Python 3.9.6
- PostgreSQL 12+
- Temporal Server
- Gemini AI API Key

### Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Mudda-AI-Workflow
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set up environment variables**
   ```bash
   cp env_example.txt .env
   # Edit .env with your configuration
   ```

4. **Configure database**
   ```bash
   # Update DATABASE_URL in .env
   DATABASE_URL=postgresql://username:password@localhost:5432/mudda_ai_db
   ```

5. **Set up Gemini AI**
   ```bash
   # Get API key from Google AI Studio
   # Add to .env file
   GEMINI_API_KEY=your_api_key_here
   ```

6. **Initialize database**
   ```bash
   python -c "from database import engine; from models import Base; Base.metadata.create_all(engine)"
   ```

## Usage

### 1. Start the API Server

```bash
python main.py
```

The API will be available at `http://localhost:8000`

### 2. Start the Temporal Worker

```bash
python temporal_worker.py
```

### 3. Run Example Usage

```bash
python example_usage.py
```

## API Endpoints

### Workflow Management

- `POST /workflows/generate` - Generate a new workflow plan
- `GET /workflows/{workflow_id}` - Get workflow details
- `GET /workflows` - List all workflows
- `POST /workflows/{workflow_id}/execute` - Execute a workflow

### Component Management

- `POST /components` - Create a new component
- `GET /components` - List all components
- `GET /components/{component_id}` - Get component details

### System

- `GET /` - Root endpoint
- `GET /health` - Health check

## Example Usage

### Generate a Workflow

```python
import requests

# Generate workflow for pothole issue
response = requests.post("http://localhost:8000/workflows/generate", json={
    "problem_statement": "Resolve pothole issue reported in Ward 22"
})

workflow = response.json()
print(f"Generated workflow: {workflow['workflow_plan']['workflow_name']}")
```

### Create a Component

```python
import requests

# Create a new API component
component_data = {
    "name": "Issue Service - Get Issue Details",
    "description": "Fetch detailed information about a reported issue",
    "type": "REST",
    "endpoint_url": "https://issue-service.gov/api/issues/{issue_id}",
    "http_method": "GET",
    "owner_service": "issue-service"
}

response = requests.post("http://localhost:8000/components", json=component_data)
```

## Workflow Structure

Generated workflows follow a DAG (Directed Acyclic Graph) structure:

```json
{
  "workflow_name": "Resolve_Pothole_Issue",
  "description": "Workflow to resolve pothole issue in Ward 22",
  "steps": [
    {
      "step_id": "fetch_issue",
      "component_id": "uuid-of-component",
      "description": "Fetch issue details",
      "inputs": {
        "path_params": {"issue_id": "{{issue_id}}"}
      },
      "outputs": ["issue_details"],
      "next": ["assign_officer"]
    },
    {
      "step_id": "assign_officer",
      "component_id": "uuid-of-assignment-component",
      "description": "Assign officer to issue",
      "inputs": {
        "request_body": {
          "issue_id": "{{issue_id}}",
          "department": "Road Maintenance"
        }
      },
      "outputs": ["assignment_confirmation"],
      "requires_approval": true,
      "next": ["notify_citizen"]
    }
  ]
}
```

## Configuration

### Environment Variables

- `DATABASE_URL`: PostgreSQL connection string
- `GEMINI_API_KEY`: Google Gemini AI API key
- `TEMPORAL_HOST`: Temporal server host (default: localhost:7233)
- `TEMPORAL_NAMESPACE`: Temporal namespace (default: default)
- `API_HOST`: API server host (default: 0.0.0.0)
- `API_PORT`: API server port (default: 8000)

## Development

### Project Structure

```
Mudda-AI-Workflow/
├── main.py                 # FastAPI application
├── models.py               # Database models
├── database.py             # Database connection
├── workflow_generator.py   # AI workflow generator
├── temporal_workflows.py   # Temporal.io integration
├── schemas.py              # Pydantic schemas
├── example_usage.py       # Example usage and tests
├── temporal_worker.py      # Temporal worker
├── requirements.txt        # Python dependencies
└── README.md              # This file
```

### Adding New Components

1. Use the API to create components:
   ```python
   POST /components
   ```

2. Or add directly to database:
   ```python
   from models import Component
   from database import SessionLocal
   
   db = SessionLocal()
   component = Component(
       name="Your Component",
       description="Component description",
       type="REST",
       endpoint_url="https://api.example.com/endpoint",
       http_method="POST",
       owner_service="your-service"
   )
   db.add(component)
   db.commit()
   ```

## Troubleshooting

### Common Issues

1. **Database Connection Error**
   - Check PostgreSQL is running
   - Verify DATABASE_URL in .env

2. **Gemini AI Error**
   - Verify GEMINI_API_KEY is set
   - Check API key is valid

3. **Temporal Connection Error**
   - Ensure Temporal server is running
   - Check TEMPORAL_HOST configuration

### Logs

- API logs: Check console output when running `python main.py`
- Temporal logs: Check Temporal server logs
- Database logs: Check PostgreSQL logs

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License.

## Support

For issues and questions:
1. Check the troubleshooting section
2. Review the example usage
3. Create an issue in the repository
