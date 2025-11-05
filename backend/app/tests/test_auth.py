"""
Tests for Authentication
"""

import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)


def test_health_check():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


def test_google_login_endpoint():
    """Test Google login endpoint exists"""
    response = client.get("/api/v1/auth/google/login")
    # Should return 200 or redirect (depending on config)
    assert response.status_code in [200, 302, 400]


def test_me_endpoint_requires_auth():
    """Test that /me endpoint requires authentication"""
    response = client.get("/api/v1/auth/me")
    assert response.status_code == 403  # Unauthorized without token

