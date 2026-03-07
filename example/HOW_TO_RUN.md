# How to Run the Example Workflow

## Prerequisites (5 minutes)

### 1. Start Temporal Server
```bash
cd backend/temporal-dev
docker-compose up -d
cd ..
```

Verify: http://localhost:8233 should load

### 2. Activate Python Environment
```bash
# Linux/Mac
source .venv/bin/activate

# Windows
.venv\Scripts\activate
```

### 3. Configure Environment
Edit `backend/.env`:
```env
# Temporal
TEMPORAL_HOST=localhost:7233
TEMPORAL_NAMESPACE=default

# Database
DATABASE_URL=sqlite:///./mudda.db

# LLM (choose one)
LLM_PROVIDER=gemini
GEMINI_API_KEY=your_actual_key_here

# Email (choose one)
EMAIL_PROVIDER=resend
RESEND_API_KEY=your_actual_key_here

# S3
S3_BUCKET_NAME=your-bucket-name
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
AWS_REGION=us-east-1
```

## Running the Example

### Option 1: Automated (Recommended)

**Linux/Mac:**
```bash
cd backend
bash example/quick_start.sh
```

**Windows:**
```bash
cd backend
example\quick_start.bat
```

This will:
1. Start the worker in the background
2. Execute the workflow
3. Show results
4. Clean up

### Option 2: Manual (Two Terminals)

**Terminal 1 - Start Worker:**
```bash
cd backend
python -m example.example_worker
```

Keep this running! You should see:
```
Starting Example Temporal Worker
Starting Temporal worker on queue 'mudda-ai-workflows'…
```

**Terminal 2 - Run Workflow:**
```bash
cd backend
python -m example.run_example_workflow
```

You should see:
```
Starting Example Workflow: Photosynthesis Document Generation
[1/4] Creating WorkflowExecution record...
[2/4] Connecting to Temporal...
[3/4] Starting workflow execution...
[4/4] Waiting for workflow completion...
```

## What Happens

### Step 1: PDF Generation (30-60 seconds)
- AI generates 300-word text about photosynthesis
- PDF is created from the text
- PDF is uploaded to S3

### Step 2: Email Notification (5-10 seconds)
- Email is composed with S3 URL
- Email is sent to shb.pndr@gmail.com

### Total Time: ~1-2 minutes

## Expected Output

```
================================================================================
WORKFLOW COMPLETED SUCCESSFULLY!
================================================================================

Workflow Status: completed
Workflow Name: Photosynthesis Document Generation and Email

--- Step Results ---

step_001_generate_pdf:
  step_id: step_001_generate_pdf
  status: completed
  file_path: /tmp/report_20240306_100115.pdf
  s3_url: https://s3.amazonaws.com/your-bucket/documents/report_20240306_100115.pdf
  filename: report_20240306_100115.pdf
  size_bytes: 15234
  ai_metadata: {'report_type': 'educational', 'report_length_chars': 2145, 'model': 'gemini'}

step_002_send_email:
  step_id: step_002_send_email
  status: completed
  channel: email
  message_id: abc123-def456-ghi789
  to: ['shb.pndr@gmail.com']
  subject: Educational Document: Understanding Photosynthesis

================================================================================
KEY OUTPUTS
================================================================================

📄 PDF Generated:
   File: /tmp/report_20240306_100115.pdf
   S3 URL: https://s3.amazonaws.com/your-bucket/documents/report_20240306_100115.pdf
   Size: 15234 bytes

📧 Email Sent:
   To: ['shb.pndr@gmail.com']
   Subject: Educational Document: Understanding Photosynthesis
   Message ID: abc123-def456-ghi789

================================================================================
```

## Verification

### 1. Check Email
- Open inbox at shb.pndr@gmail.com
- Look for email with subject "Educational Document: Understanding Photosynthesis"
- Email should contain S3 URL

### 2. Check PDF
- Click S3 URL from email or output
- PDF should download
- Open PDF - should be about photosynthesis, ~300 words

### 3. Check Temporal UI
- Visit http://localhost:8233
- Click "Workflows"
- Find workflow: `mudda-workflow-1`
- Status should be "Completed"
- All activities should show green checkmarks

### 4. Check Database
```bash
cd backend
sqlite3 mudda.db "SELECT id, issue_id, status FROM workflow_executions;"
```

Should show:
```
1|example_photosynthesis_001|completed
```

## Troubleshooting

### Error: Connection refused to localhost:7233
**Problem:** Temporal server not running

**Solution:**
```bash
cd backend/temporal-dev
docker-compose up -d
# Wait 10 seconds
docker ps  # Should show temporal containers
```

### Error: LLM provider not configured
**Problem:** Missing or invalid LLM API key

**Solution:**
1. Check `.env` has `LLM_PROVIDER=gemini` (or `bedrock`)
2. Verify `GEMINI_API_KEY` is set and valid
3. Test: `python -c "import os; from dotenv import load_dotenv; load_dotenv(); print(os.getenv('GEMINI_API_KEY'))"`

### Error: Email provider authentication failed
**Problem:** Missing or invalid email API key

**Solution:**
1. Check `.env` has `EMAIL_PROVIDER=resend` (or other)
2. Verify `RESEND_API_KEY` is set and valid
3. Ensure sender email is verified in provider dashboard

### Error: Access Denied (S3)
**Problem:** Invalid AWS credentials or permissions

**Solution:**
1. Verify AWS credentials in `.env`
2. Check bucket exists: `aws s3 ls s3://your-bucket-name`
3. Verify IAM permissions include `s3:PutObject`

### Worker shows no activity
**Problem:** Worker not receiving tasks

**Solution:**
1. Ensure worker is running (Terminal 1)
2. Check worker logs for "Starting Temporal worker"
3. Verify workflow was started (Terminal 2 shows workflow ID)
4. Check Temporal UI for workflow status

## Stopping

### Automated Mode
- Script stops automatically after completion

### Manual Mode
- Terminal 2: Workflow completes automatically
- Terminal 1: Press `Ctrl+C` to stop worker

### Stop Temporal Server (Optional)
```bash
cd backend/temporal-dev
docker-compose down
```

## Next Steps

After successful run:

1. **Modify the workflow**
   - Edit `example/example_workflow_plan.py`
   - Change the problem statement
   - Add more steps
   - Test different activities

2. **Add approval steps**
   ```python
   {
       "step_id": "step_003_approval",
       "activity_id": "human_feedback_activity",
       "requires_approval": True,
       "inputs": {...}
   }
   ```

3. **Try other activities**
   - `contact_plumber`
   - `update_issue_activity`
   - `human_verification_activity`

4. **Explore the code**
   - `workflows/mudda_workflow.py` - Workflow logic
   - `activities/` - Activity implementations
   - `temporal/worker.py` - Worker setup
   - `temporal/client.py` - Client setup

## Quick Reference

| Command | Purpose |
|---------|---------|
| `docker-compose up -d` | Start Temporal |
| `python -m example.example_worker` | Start worker |
| `python -m example.run_example_workflow` | Run workflow |
| `docker ps` | Check Temporal status |
| `curl http://localhost:8233` | Test Temporal UI |

## Success Checklist

- [ ] Temporal server running
- [ ] Worker started without errors
- [ ] Workflow executed successfully
- [ ] PDF generated and uploaded
- [ ] Email sent and received
- [ ] Workflow visible in Temporal UI
- [ ] Database shows completed status

## Need More Help?

- **Quick start**: [QUICKSTART.md](QUICKSTART.md)
- **Detailed testing**: [MANUAL_TEST.md](MANUAL_TEST.md)
- **Prerequisites**: [CHECKLIST.md](CHECKLIST.md)
- **Architecture**: [ARCHITECTURE.md](ARCHITECTURE.md)
- **Full docs**: [README.md](README.md)
