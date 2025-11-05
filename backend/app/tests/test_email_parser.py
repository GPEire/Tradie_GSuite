"""
Tests for Email Parser
"""

import pytest
from datetime import datetime
from app.services.email_parser import EmailParser, parse_gmail_message


def test_extract_header():
    """Test header extraction"""
    headers = [
        {"name": "Subject", "value": "Test Email"},
        {"name": "From", "value": "test@example.com"},
        {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"}
    ]
    
    assert EmailParser.extract_header(headers, "Subject") == "Test Email"
    assert EmailParser.extract_header(headers, "subject") == "Test Email"  # Case insensitive
    assert EmailParser.extract_header(headers, "From") == "test@example.com"
    assert EmailParser.extract_header(headers, "Nonexistent") is None


def test_decode_body():
    """Test body decoding"""
    # Base64 encoded "Hello World"
    encoded = "SGVsbG8gV29ybGQ="
    decoded = EmailParser.decode_body(encoded, "base64")
    assert decoded == "Hello World"


def test_parse_email_address():
    """Test email address parsing"""
    # Name with email
    result = EmailParser.parse_email_address('John Doe <john@example.com>')
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"
    
    # Just email
    result = EmailParser.parse_email_address('john@example.com')
    assert result["name"] == ""
    assert result["email"] == "john@example.com"
    
    # Quoted name
    result = EmailParser.parse_email_address('"John Doe" <john@example.com>')
    assert result["name"] == "John Doe"
    assert result["email"] == "john@example.com"


def test_parse_addresses():
    """Test parsing multiple addresses"""
    addresses = "John <john@example.com>, Jane <jane@example.com>"
    parsed = EmailParser.parse_addresses(addresses)
    assert len(parsed) == 2
    assert parsed[0]["email"] == "john@example.com"
    assert parsed[1]["email"] == "jane@example.com"


def test_parse_date():
    """Test date parsing"""
    date_str = "Mon, 1 Jan 2024 12:00:00 +0000"
    parsed = EmailParser.parse_date(date_str)
    assert isinstance(parsed, datetime)
    assert parsed.year == 2024
    assert parsed.month == 1
    assert parsed.day == 1


def test_html_to_text():
    """Test HTML to text conversion"""
    html = "<p>Hello <strong>World</strong></p>"
    text = EmailParser.html_to_text(html)
    assert "Hello" in text
    assert "World" in text
    assert "<" not in text  # HTML tags removed


def test_parse_message_basic():
    """Test parsing a basic Gmail message"""
    message = {
        "id": "123",
        "threadId": "456",
        "labelIds": ["INBOX"],
        "snippet": "Test snippet",
        "sizeEstimate": 1024,
        "historyId": "789",
        "payload": {
            "headers": [
                {"name": "Subject", "value": "Test Subject"},
                {"name": "From", "value": "sender@example.com"},
                {"name": "To", "value": "recipient@example.com"},
                {"name": "Date", "value": "Mon, 1 Jan 2024 12:00:00 +0000"}
            ],
            "body": {
                "data": "SGVsbG8gV29ybGQ=",  # "Hello World" in base64
                "size": 11
            },
            "mimeType": "text/plain"
        }
    }
    
    parsed = parse_gmail_message(message)
    
    assert parsed["id"] == "123"
    assert parsed["thread_id"] == "456"
    assert parsed["subject"] == "Test Subject"
    assert parsed["from"]["email"] == "sender@example.com"
    assert "Hello World" in parsed["body_text"]


def test_extract_attachments():
    """Test attachment extraction"""
    payload = {
        "parts": [
            {
                "mimeType": "text/plain",
                "body": {"data": "SGVsbG8="}
            },
            {
                "filename": "document.pdf",
                "mimeType": "application/pdf",
                "body": {
                    "attachmentId": "att123",
                    "size": 1024
                }
            }
        ]
    }
    
    attachments = EmailParser.extract_attachments(payload)
    assert len(attachments) == 1
    assert attachments[0]["filename"] == "document.pdf"
    assert attachments[0]["attachment_id"] == "att123"

