import pytest
import resend
from unittest.mock import MagicMock
from infrastructure.email_adapter import EmailAdapter

@pytest.fixture
def mock_settings(mocker):
    mock = mocker.patch("infrastructure.email_adapter.settings")
    mock.RESEND_API_KEY = "re_test_key"
    mock.EMAIL_FROM_ADDRESS = "noreply@test.com"
    mock.EMAIL_FROM_NAME = "Test Mudda"
    return mock

@pytest.fixture
def mock_resend(mocker):
    return mocker.patch("resend.Emails.send")

@pytest.mark.asyncio
async def test_send_email_success(mock_settings, mock_resend):
    # Setup
    adapter = EmailAdapter()
    mock_resend.return_value = {"id": "msg_123"}
    
    payload = {
        "to": "user@example.com",
        "subject": "Test Subject",
        "body": "Test Body"
    }
    
    # Execute
    result = await adapter.send_email(payload)
    
    # Verify
    assert result["message_id"] == "msg_123"
    assert result["status"] == "sent"
    assert result["to"] == ["user@example.com"]
    assert result["subject"] == "Test Subject"
    
    mock_resend.assert_called_once_with({
        "from": "Test Mudda <noreply@test.com>",
        "to": ["user@example.com"],
        "subject": "Test Subject",
        "text": "Test Body"
    })

@pytest.mark.asyncio
async def test_send_email_missing_to(mock_settings):
    adapter = EmailAdapter()
    with pytest.raises(ValueError, match="'to' field is required"):
        await adapter.send_email({"subject": "foo", "body": "bar"})

@pytest.mark.asyncio
async def test_send_email_missing_subject(mock_settings):
    adapter = EmailAdapter()
    with pytest.raises(ValueError, match="'subject' field is required"):
        await adapter.send_email({"to": "user@example.com", "body": "bar"})

@pytest.mark.asyncio
async def test_send_email_missing_body(mock_settings):
    adapter = EmailAdapter()
    with pytest.raises(ValueError, match=r"either 'body' \(text\) or 'html' is required"):
        await adapter.send_email({"to": "user@example.com", "subject": "foo"})

def test_recipient_normalisation(mock_settings):
    adapter = EmailAdapter()
    assert adapter._normalise_recipients(" test@example.com ") == ["test@example.com"]
    assert adapter._normalise_recipients([" a@b.com", "c@d.com "]) == ["a@b.com", "c@d.com"]
    assert adapter._normalise_recipients(None) == []
    assert adapter._normalise_recipients("") == []

@pytest.mark.asyncio
async def test_send_email_html(mock_settings, mock_resend):
    adapter = EmailAdapter()
    mock_resend.return_value = {"id": "msg_html"}
    
    payload = {
        "to": "user@example.com",
        "subject": "HTML Test",
        "html": "<h1>Hello</h1>"
    }
    
    await adapter.send_email(payload)
    
    mock_resend.assert_called_once_with({
        "from": "Test Mudda <noreply@test.com>",
        "to": ["user@example.com"],
        "subject": "HTML Test",
        "html": "<h1>Hello</h1>"
    })
