import pytest
import resend
import os
from infrastructure.email_adapter import EmailAdapter
from config import settings

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def mock_settings(mocker):
    """Mocks settings to return predictable test values."""
    mock = mocker.patch("infrastructure.email_adapter.settings")
    mock.RESEND_API_KEY = settings.RESEND_API_KEY
    mock.EMAIL_FROM_ADDRESS = settings.EMAIL_FROM_ADDRESS
    mock.EMAIL_FROM_NAME = settings.EMAIL_FROM_NAME
    return mock

@pytest.fixture
def mock_resend_send(mocker):
    """Mocks the Resend SDK's send method."""
    return mocker.patch("resend.Emails.send")

# --------------------------------------------------------------------------
# Unit Tests (Mocked)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_unit_send_email_success(mock_settings, mock_resend_send):
    """Verify the adapter correctly formats and sends an email (mocked)."""
    adapter = EmailAdapter()
    mock_resend_send.return_value = {"id": "msg_mock_123"}
    
    payload = {
        "to": "shb.pndr@gmail.com",
        "subject": "Unit Test Subject",
        "body": "This is a mocked unit test body."
    }
    
    result = await adapter.send_email(payload)
    
    # Verify adapter return value
    assert result["message_id"] == "msg_mock_123"
    assert result["status"] == "sent"
    assert result["to"] == ["shb.pndr@gmail.com"]
    
    # Verify Resend SDK was called with expected arguments from the mock!
    # Note: Using f-string to match the logic in the adapter
    expected_from = f"{mock_settings.EMAIL_FROM_NAME} <{mock_settings.EMAIL_FROM_ADDRESS}>"
    
    mock_resend_send.assert_called_once_with({
        "from": expected_from,
        "to": ["shb.pndr@gmail.com"],
        "subject": "Unit Test Subject",
        "text": "This is a mocked unit test body."
    })

@pytest.mark.asyncio
async def test_unit_send_email_html(mock_settings, mock_resend_send):
    """Verify HTML content is prioritised correctly."""
    adapter = EmailAdapter()
    mock_resend_send.return_value = {"id": "msg_html_123"}
    
    payload = {
        "to": "shb.pndr@gmail.com",
        "subject": "HTML Test",
        "html": "<strong>Bold Content</strong>"
    }
    
    await adapter.send_email(payload)
    
    mock_resend_send.assert_called_once()
    args = mock_resend_send.call_args[0][0]
    assert args["html"] == "<strong>Bold Content</strong>"
    assert "text" not in args

@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field, payload", [
    ("to", {"subject": "no to", "body": "body"}),
    ("subject", {"to": "a@b.com", "body": "body"}),
    ("body/html", {"to": "a@b.com", "subject": "no body"}),
])
async def test_unit_validation_errors(mock_settings, missing_field, payload):
    """Verify that missing required fields raise ValueError."""
    adapter = EmailAdapter()
    with pytest.raises(ValueError):
        await adapter.send_email(payload)

def test_unit_recipient_normalisation(mock_settings):
    """Test the internal recipient cleaning logic."""
    adapter = EmailAdapter()
    assert adapter._normalise_recipients(" test@example.com ") == ["test@example.com"]
    assert adapter._normalise_recipients([" a@b.com ", " c@d.com"]) == ["a@b.com", "c@d.com"]
    assert adapter._normalise_recipients(None) == []

# --------------------------------------------------------------------------
# Integration Test (Real Email)
# --------------------------------------------------------------------------

# Skip this test unless a valid Resend API key is provided and not the placeholder.
HAS_REAL_KEY = (
    settings.RESEND_API_KEY 
    and not settings.RESEND_API_KEY.startswith("re_your_api_key")
    and settings.RESEND_API_KEY != ""
)

@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_REAL_KEY, reason="RESEND_API_KEY not configured in .env")
async def test_integration_send_real_email():
    """
    REAL WORKING TEST: Sends an actual email via the Resend API.
    
    NOTE: Fresh Resend accounts can only send from 'onboarding@resend.dev'
    to the account owner's email address (project.mudda@gmail.com).
    """
    # Try sending to the user's requested address first, fallback to owner if needed.
    # From the error logs, we know the owner is project.mudda@gmail.com
    owner_email = "project.mudda@gmail.com"
    target_emails = ["shb.pndr@gmail.com", owner_email]
    
    adapter = EmailAdapter()
    
    last_error = None
    for email in target_emails:
        print(f"\nAttempting to send real email to: {email}...")
        
        payload = {
            "to": email,
            "subject": f"Mudda AI: Real Working Test ({email})",
            "html": f"""
            <h2>Mudda AI Workflow - Integration Test</h2>
            <p>This is a real email sent via the <strong>Resend API</strong> adapter.</p>
            <p><strong>To:</strong> {email}</p>
            <p><strong>From:</strong> {settings.EMAIL_FROM_ADDRESS}</p>
            <p>Sent at: 2026-02-26</p>
            <hr/>
            <p><small>If you received this, the adapter is working perfectly.</small></p>
            """
        }
        
        try:
            result = await adapter.send_email(payload)
            print(f"✅ Success! Message ID: {result['message_id']}")
            return # Test passes
        except resend.exceptions.ResendError as e:
            last_error = e
            print(f"❌ Failed to send to {email}: {e}")
            if "verify your domain" in str(e).lower():
                print("ℹ️ Resend restriction: Testing emails are limited to the account owner until a domain is verified.")
                continue
    
    pytest.fail(f"Real email sending failed for all targets. Last error: {last_error}")
