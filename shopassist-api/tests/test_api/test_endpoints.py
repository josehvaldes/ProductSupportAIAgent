"""
Tests for API endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from shopassist_api.main import app

client = TestClient(app)


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/api/v1/health")
    assert response.status_code == 200
    
    data = response.json()
    assert data["status"] == "healthy"
    assert data["service"] == "shop-assistant-api"
    assert "timestamp" in data


def test_chat_endpoint():
    """Test the chat endpoint."""
    test_message = {
        "message": "Hello, I'm looking for headphones",
        "user_id": "test_user"
    }
    
    response = client.post("/api/v1/chat", json=test_message)
    assert response.status_code == 200
    
    data = response.json()
    assert "message" in data
    assert "conversation_id" in data
    assert isinstance(data.get("suggestions"), list)


def test_chat_endpoint_empty_message():
    """Test chat endpoint with empty message."""
    test_message = {
        "message": "",
        "user_id": "test_user"
    }
    
    response = client.post("/api/v1/chat", json=test_message)
    # Should still return 200 but handle gracefully
    assert response.status_code == 200
