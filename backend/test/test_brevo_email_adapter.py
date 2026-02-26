import pytest
from unittest.mock import AsyncMock, MagicMock
import httpx
from infrastructure.email.brevo_email_adapter import BrevoEmailAdapter
from config import settings

# --------------------------------------------------------------------------
# Fixtures
# --------------------------------------------------------------------------

@pytest.fixture
def mock_httpx_client(mocker):
    """Mocks the httpx.AsyncClient."""
    mock_client = AsyncMock(spec=httpx.AsyncClient)
    # Mock the context manager __aenter__ to return the mock_client
    mocker.patch("httpx.AsyncClient", return_value=mock_client)
    mock_client.__aenter__.return_value = mock_client
    return mock_client

# --------------------------------------------------------------------------
# Unit Tests (Mocked)
# --------------------------------------------------------------------------

@pytest.mark.asyncio
async def test_brevo_send_email_success(mock_httpx_client):
    """Verify Brevo adapter correctly formats and sends an email (mocked)."""
    adapter = BrevoEmailAdapter()
    
    # Mock a successful response from Brevo
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 201
    mock_response.json.return_value = {"messageId": "brevo_msg_123"}
    mock_httpx_client.post.return_value = mock_response
    
    payload = {
        "to": "shb.pndr@gmail.com",
        "subject": "Brevo Unit Test",
        "body": "Hello from Brevo mock test",
        "from_name": "Test Sender",
        "from_email": "sender@example.com"
    }
    
    result = await adapter.send_email(payload)
    
    # Verify adapter return value
    assert result["message_id"] == "brevo_msg_123"
    assert result["status"] == "sent"
    assert result["to"] == ["shb.pndr@gmail.com"]
    
    # Verify httpx.AsyncClient.post was called with expected arguments
    assert mock_httpx_client.post.called
    args, kwargs = mock_httpx_client.post.call_args
    
    # Check headers
    headers = kwargs["headers"]
    assert headers["api-key"] == settings.BREVO_API_KEY
    
    # Check JSON payload
    json_data = kwargs["json"]
    assert json_data["sender"] == {"name": "Test Sender", "email": "sender@example.com"}
    assert json_data["to"] == [{"email": "shb.pndr@gmail.com"}]
    assert json_data["subject"] == "Brevo Unit Test"
    assert json_data["textContent"] == "Hello from Brevo mock test"

@pytest.mark.asyncio
async def test_brevo_send_email_api_error(mock_httpx_client):
    """Verify that Brevo API errors raise RuntimeError with status code."""
    adapter = BrevoEmailAdapter()
    
    # Mock a 401 Unauthorized response
    mock_response = MagicMock(spec=httpx.Response)
    mock_response.status_code = 401
    mock_response.text = "Unauthorized"
    mock_httpx_client.post.return_value = mock_response
    
    payload = {
        "to": "shb.pndr@gmail.com",
        "subject": "Error Test",
        "body": "Body"
    }
    
    with pytest.raises(RuntimeError) as excinfo:
        await adapter.send_email(payload)
    
    assert "Brevo send failed (401)" in str(excinfo.value)

@pytest.mark.asyncio
@pytest.mark.parametrize("missing_field, payload", [
    ("to", {"subject": "no to", "body": "body"}),
    ("subject", {"to": "a@b.com", "body": "body"}),
    ("body/html", {"to": "a@b.com", "subject": "no body"}),
])
async def test_brevo_validation_errors(missing_field, payload):
    """Verify that missing required fields raise ValueError in Brevo adapter."""
    adapter = BrevoEmailAdapter()
    with pytest.raises(ValueError) as excinfo:
        await adapter.send_email(payload)
    assert "BrevoEmailAdapter.send_email" in str(excinfo.value)

def test_brevo_recipient_normalisation():
    """Test the internal recipient cleaning logic (inherited or copied)."""
    adapter = BrevoEmailAdapter()
    assert adapter._normalise_recipients(" test@example.com ") == ["test@example.com"]
    assert adapter._normalise_recipients([" a@b.com ", " c@d.com"]) == ["a@b.com", "c@d.com"]
    assert adapter._normalise_recipients(None) == []

# --------------------------------------------------------------------------
# Integration Test (Real Email)
# --------------------------------------------------------------------------

HAS_BREVO_KEY = (
    settings.BREVO_API_KEY 
    and len(settings.BREVO_API_KEY) > 20
)

@pytest.mark.asyncio
@pytest.mark.skipif(not HAS_BREVO_KEY, reason="BREVO_API_KEY not configured in .env")
async def test_integration_brevo_real_email():
    """
    Integration test for sending a real email via Brevo.
    """
    # Using the email address provided in the unit tests
    target_email = "shb.pndr@gmail.com" 
    
    adapter = BrevoEmailAdapter()
    
    # NOTE: Brevo REQUIRES the sender email to be verified in your Brevo account.
    # If settings.EMAIL_FROM_ADDRESS (or payload['from_email']) is not verified, 
    # Brevo might reject the call or accept it but never deliver.
    
    payload = {
        "to": target_email,
        "subject": "Mudda AI: Brevo Integration Test",
        "html": f"""
        <h2>Mudda AI Workflow - Brevo Test</h2>
        <p>This is a real email sent via the <strong>Brevo API</strong> adapter.</p>
        <p><strong>Target:</strong> {target_email}</p>
        <p><strong>Sender:</strong> {settings.EMAIL_FROM_ADDRESS}</p>
        <p>Sent at: 2026-02-26</p>
        <hr/>
        <p><small>If you received this, the Brevo factory pattern is working perfectly.</small></p>
        <p><small>Note: If you don't receive this, check if '{settings.EMAIL_FROM_ADDRESS}' is a verified sender in your Brevo dashboard.</small></p>
        """
    }
    
    print(f"\nAttempting to send real Brevo email to: {target_email}...")
    print(f"Using Sender: {settings.EMAIL_FROM_ADDRESS}")
    
    try:
        result = await adapter.send_email(payload)
        print(f"✅ Brevo accepted the request! Message ID: {result['message_id']}")
        print(f"ℹ️ If you still don't see it in {target_email}, verify that your Brevo account is active and '{settings.EMAIL_FROM_ADDRESS}' is a verified sender.")
        assert "message_id" in result
    except Exception as e:
        pytest.fail(f"Real Brevo email sending failed: {e}")
