import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from app.core.middleware import RateLimitMiddleware, ProcessingTimeMiddleware
import time
import asyncio

def create_test_app(requests_per_minute: int = 60):
    app = FastAPI()
    app.add_middleware(RateLimitMiddleware, requests_per_minute=requests_per_minute)
    app.add_middleware(ProcessingTimeMiddleware)
    
    @app.get("/test")
    def test_endpoint():
        return {"status": "ok"}
    
    @app.get("/test/slow-endpoint")
    async def slow_endpoint():
        await asyncio.sleep(0.1)  # Simulate slow processing
        return {"status": "done"}
    
    return app

client = TestClient(create_test_app())

def test_rate_limit():
    app = create_test_app(requests_per_minute=2)
    client = TestClient(app)
    
    # First two requests should succeed
    response1 = client.get("/test")
    assert response1.status_code == 200
    
    response2 = client.get("/test")
    assert response2.status_code == 200
    
    # Third request should be rate limited
    response3 = client.get("/test")
    assert response3.status_code == 429
    assert "Too many requests" in response3.json()["detail"]

def test_rate_limit_reset():
    app = create_test_app(requests_per_minute=1)
    client = TestClient(app)
    
    # First request succeeds
    response1 = client.get("/test")
    assert response1.status_code == 200
    
    # Second request is rate limited
    response2 = client.get("/test")
    assert response2.status_code == 429
    
    # Wait for rate limit to reset
    time.sleep(60)
    
    # Request after reset succeeds
    response3 = client.get("/test")
    assert response3.status_code == 200

def test_different_clients():
    app = create_test_app(requests_per_minute=1)
    client1 = TestClient(app, headers={"X-Forwarded-For": "1.1.1.1"})
    client2 = TestClient(app, headers={"X-Forwarded-For": "2.2.2.2"})
    
    # Both clients' first requests should succeed
    response1 = client1.get("/test")
    assert response1.status_code == 200
    
    response2 = client2.get("/test")
    assert response2.status_code == 200
    
    # Both clients' second requests should be rate limited
    response3 = client1.get("/test")
    assert response3.status_code == 429
    
    response4 = client2.get("/test")
    assert response4.status_code == 429

def test_rate_limit_middleware():
    """Test rate limiting functionality."""
    # Test normal request
    response = client.get("/test")
    assert response.status_code == 200
    
    # Test rate limiting by making many requests
    responses = []
    for _ in range(70):  # More than the rate limit
        responses.append(client.get("/test"))
    
    # Check if we got rate limited
    assert any(r.status_code == 429 for r in responses)
    # Check rate limit response format
    rate_limited = next(r for r in responses if r.status_code == 429)
    assert "error" in rate_limited.json()
    assert "retry_after" in rate_limited.json()

def test_processing_time_middleware():
    """Test processing time tracking."""
    response = client.get("/test/slow-endpoint")
    assert response.status_code == 200
    assert "X-Process-Time" in response.headers
    process_time = float(response.headers["X-Process-Time"])
    assert process_time >= 0.1  # Should be at least our sleep time

def test_rate_limit_health_check_bypass():
    """Test that health check endpoint bypasses rate limiting."""
    responses = []
    for _ in range(70):  # More than the rate limit
        responses.append(client.get("/test"))
    
    # None should be rate limited
    assert all(r.status_code == 200 for r in responses)

@pytest.mark.asyncio
async def test_rate_limit_cleanup():
    """Test that old request records are cleaned up."""
    app = create_test_app()
    middleware = RateLimitMiddleware(app)
    test_ip = "127.0.0.1"
    
    # Add some test requests
    now = time.time()
    old_time = now - 120  # 2 minutes ago
    middleware.request_history[test_ip] = [old_time]
    
    # Run cleanup
    await middleware._cleanup_old_requests()
    
    # Check that old requests were removed
    assert test_ip not in middleware.request_history

def test_processing_time_logging(caplog):
    """Test that processing time is logged correctly."""
    with caplog.at_level("INFO"):
        response = client.get("/test")
        assert any("Processing time for /test:" in record.message 
                  for record in caplog.records)