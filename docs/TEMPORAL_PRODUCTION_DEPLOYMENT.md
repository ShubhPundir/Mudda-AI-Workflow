# Production Deployment Guide

This guide explains how to deploy your Temporal workflow system to production.

## Architecture Overview

### Local Development
```
┌─────────────────────────────────────────────────┐
│ Temporal Server (local)                         │
│ → temporal server start-dev                     │
├─────────────────────────────────────────────────┤
│ Worker (your machine)                           │
│ → python temporal_worker.py                     │
├─────────────────────────────────────────────────┤
│ API Server (your machine)                       │
│ → uvicorn main:app                              │
├─────────────────────────────────────────────────┤
│ Database (local PostgreSQL)                     │
└─────────────────────────────────────────────────┘
```

### Production
```
┌─────────────────────────────────────────────────┐
│ Temporal Cloud ☁️                               │
│ → Managed service (no setup needed)             │
│ → https://cloud.temporal.io                     │
├─────────────────────────────────────────────────┤
│ Worker (deployed as service)                    │
│ → Docker container / K8s pod                    │
│ → Connects to Temporal Cloud                    │
│ → Executes activities                           │
├─────────────────────────────────────────────────┤
│ API Server (deployed as service)                │
│ → Docker container / K8s pod                    │
│ → Handles HTTP requests                         │
│ → Triggers workflows via Temporal client        │
├─────────────────────────────────────────────────┤
│ Database (managed PostgreSQL)                   │
│ → AWS RDS / Azure Database / etc.               │
└─────────────────────────────────────────────────┘
```

## Production Flow

### 1. User Request → API
```
POST /workflows/{workflow_id}/execute
```

### 2. API → Database
- Reads `WorkflowPlan` from database
- Creates `WorkflowExecution` record
- Gets execution UUID

### 3. API → Temporal Cloud
- Connects to Temporal Cloud
- Starts workflow with plan from DB
- Returns execution ID to user

### 4. Temporal Cloud → Worker
- Temporal routes workflow to available worker
- Worker executes activities sequentially
- Updates execution status in database

### 5. Worker → Database
- Updates `WorkflowExecution` status
- Stores results in `execution_data` JSONB field

## Environment Configuration

### Development (.env)
```bash
# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Database
DATABASE_URL=postgresql+asyncpg://postgres:password@localhost:5432/mudda_ai

# API
API_HOST=0.0.0.0
API_PORT=8000
```

### Production (.env)
```bash
# Temporal Cloud
TEMPORAL_HOST=your-namespace.tmprl.cloud:7233
TEMPORAL_NAMESPACE=your-namespace
TEMPORAL_TLS_CERT=/path/to/client.pem
TEMPORAL_TLS_KEY=/path/to/client-key.pem

# Database (managed)
DATABASE_URL=postgresql+asyncpg://user:pass@prod-db.region.rds.amazonaws.com:5432/mudda_ai

# API
API_HOST=0.0.0.0
API_PORT=8000

# External Services
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
OPENAI_API_KEY=your_key
# ... other service keys
```

## Deployment Steps

### 1. Set Up Temporal Cloud

1. Sign up at https://cloud.temporal.io
2. Create a namespace
3. Download TLS certificates
4. Note your namespace URL

### 2. Set Up Database

```sql
-- Create database
CREATE DATABASE mudda_ai;

-- Create schemas
CREATE SCHEMA workflow;
CREATE SCHEMA public;

-- Run migrations (create all tables)
-- See backend/models/ for table definitions
```

### 3. Deploy Worker

The worker MUST be running for workflows to execute.

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt

CMD ["python", "temporal_worker.py"]
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: temporal-worker
spec:
  replicas: 3  # Scale based on load
  selector:
    matchLabels:
      app: temporal-worker
  template:
    metadata:
      labels:
        app: temporal-worker
    spec:
      containers:
      - name: worker
        image: your-registry/temporal-worker:latest
        env:
        - name: TEMPORAL_HOST
          value: "your-namespace.tmprl.cloud:7233"
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: db-credentials
              key: url
```

### 4. Deploy API Server

**Docker:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY backend/ /app/
RUN pip install -r requirements.txt

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

**Kubernetes:**
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: api-server
spec:
  replicas: 2
  selector:
    matchLabels:
      app: api-server
  template:
    metadata:
      labels:
        app: api-server
    spec:
      containers:
      - name: api
        image: your-registry/api-server:latest
        ports:
        - containerPort: 8000
        env:
        - name: TEMPORAL_HOST
          value: "your-namespace.tmprl.cloud:7233"
```

## Production Workflow Flow

### Step 1: Generate Workflow Plan (AI)
```bash
POST /workflows/generate
{
  "problem_statement": "Water leak at 123 Main St"
}

Response:
{
  "workflow_id": "uuid-here",
  "workflow_plan": { ... },
  "status": "DRAFT"
}
```

### Step 2: Execute Workflow
```bash
POST /workflows/{workflow_id}/execute
{
  "execution_data": {
    "issue_id": "ISSUE-001",
    "priority": "high"
  }
}

Response:
{
  "execution_id": "uuid-here",
  "workflow_plan_id": "uuid-here",
  "temporal_workflow_id": "mudda-workflow-uuid",
  "status": "pending"
}
```

### Step 3: Monitor Execution
```bash
GET /workflows/executions/{execution_id}

Response:
{
  "id": "uuid-here",
  "status": "running",  # or "completed", "failed"
  "execution_data": { ... },
  "started_at": "2026-03-01T12:00:00Z",
  "completed_at": null
}
```

## Scaling Considerations

### Worker Scaling
- Workers are stateless and can be scaled horizontally
- Each worker polls Temporal for tasks
- Scale based on workflow volume and activity duration
- Recommended: Start with 3 workers, monitor queue depth

### API Scaling
- API servers are stateless
- Scale based on HTTP request volume
- Use load balancer for distribution

### Database
- Use connection pooling
- Monitor query performance
- Consider read replicas for heavy read workloads

## Monitoring

### Temporal Cloud Dashboard
- Workflow execution metrics
- Task queue depth
- Worker health
- Failure rates

### Application Metrics
- Worker activity execution times
- Database query performance
- API response times
- Error rates

### Logging
```python
# Worker logs
logger.info("Activity started", extra={
    "activity": "send_notification",
    "execution_id": execution_id
})

# API logs
logger.info("Workflow triggered", extra={
    "workflow_id": workflow_id,
    "user_id": user_id
})
```

## Security

### Temporal Cloud
- Use TLS certificates for authentication
- Rotate certificates regularly
- Use namespace-level access control

### Database
- Use connection encryption (SSL)
- Rotate credentials regularly
- Use IAM authentication where possible

### API
- Use API keys or OAuth
- Rate limiting
- Input validation

## Troubleshooting

### Worker Not Connecting
```bash
# Check environment variables
echo $TEMPORAL_HOST
echo $TEMPORAL_NAMESPACE

# Test connection
python -c "from temporal.worker import TemporalWorkerManager; import asyncio; asyncio.run(TemporalWorkerManager()._connect())"
```

### Workflows Not Executing
1. Check worker is running and connected
2. Verify task queue name matches
3. Check Temporal Cloud dashboard for errors
4. Review worker logs

### Database Connection Issues
1. Verify DATABASE_URL is correct
2. Check network connectivity
3. Verify credentials
4. Check connection pool settings

## Cost Optimization

### Temporal Cloud
- Pay per action (workflow/activity execution)
- Optimize workflow design to minimize actions
- Use activity heartbeats for long-running tasks

### Workers
- Right-size worker instances
- Use auto-scaling based on queue depth
- Consider spot instances for non-critical workloads

### Database
- Use appropriate instance size
- Enable query caching
- Archive old execution records

## Backup and Recovery

### Database Backups
- Automated daily backups
- Point-in-time recovery
- Test restore procedures

### Workflow State
- Temporal maintains workflow state
- No additional backup needed
- Workflow history retained per retention policy

## Next Steps

1. ✅ Set up Temporal Cloud account
2. ✅ Configure production database
3. ✅ Deploy worker service
4. ✅ Deploy API service
5. ✅ Set up monitoring and alerts
6. ✅ Test end-to-end workflow execution
7. ✅ Document runbooks for common issues
