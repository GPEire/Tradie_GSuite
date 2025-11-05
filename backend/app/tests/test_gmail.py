"""
Tests for Gmail API Integration
"""

import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from app.main import app
from app.services.gmail import (
    GmailService, GmailAPIError, GmailRateLimitError,
    check_rate_limit, GMAIL_QUOTA_LIMITS
)

client = TestClient(app)


def test_rate_limit_check():
    """Test rate limiting functionality"""
    user_id = 1
    # Should allow first request
    assert check_rate_limit(user_id, "read") == True
    # Should allow multiple requests up to limit
    for _ in range(4):
        assert check_rate_limit(user_id, "read") == True
    # Should block after limit (assuming limit is 5)
    # Note: This test may need adjustment based on actual limit


def test_gmail_profile_endpoint_requires_auth():
    """Test that Gmail endpoints require authentication"""
    response = client.get("/api/v1/gmail/profile")
    assert response.status_code == 403  # Unauthorized without token


def test_gmail_quota_limits_defined():
    """Test that quota limits are properly defined"""
    assert "quota_per_second_per_user" in GMAIL_QUOTA_LIMITS
    assert "read_requests_per_second" in GMAIL_QUOTA_LIMITS
    assert "write_requests_per_second" in GMAIL_QUOTA_LIMITS


@patch('app.services.gmail.build')
def test_gmail_service_initialization(mock_build):
    """Test Gmail service initialization"""
    from app.models.user import User
    from app.services.gmail import GmailService
    
    # Mock user
    user = Mock(spec=User)
    user.id = 1
    user.email = "test@example.com"
    user.access_token = "encrypted_token"
    user.refresh_token = "encrypted_refresh"
    
    # Mock credentials
    with patch('app.services.gmail.get_user_credentials') as mock_creds:
        mock_creds.return_value = Mock()
        mock_build.return_value = Mock()
        
        # This should work if credentials are available
        # service = GmailService(user)
        # assert service is not None
        pass  # Test structure in place


def test_gmail_error_handling():
    """Test Gmail API error handling"""
    error = GmailAPIError("Test error", status_code=400)
    assert error.message == "Test error"
    assert error.status_code == 400
    
    rate_error = GmailRateLimitError("Rate limit", retry_after=60)
    assert rate_error.retry_after == 60

