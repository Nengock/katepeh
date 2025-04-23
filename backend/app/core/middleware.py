from fastapi import Request, HTTPException
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from datetime import datetime, timedelta
from collections import defaultdict
import asyncio
from .config import get_settings
from .errors import KTPProcessingError
import logging

logger = logging.getLogger(__name__)
settings = get_settings()

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests_per_minute = settings.RATE_LIMIT_PER_MINUTE
        self.request_history = defaultdict(list)
        self.cleanup_task = None
        
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        now = datetime.now()
        
        # Skip rate limiting for health check endpoint
        if request.url.path.endswith('/health'):
            return await call_next(request)
        
        # Clean old requests
        self.request_history[client_ip] = [
            req_time for req_time in self.request_history[client_ip]
            if now - req_time < timedelta(minutes=1)
        ]
        
        # Check rate limit
        if len(self.request_history[client_ip]) >= self.requests_per_minute:
            logger.warning(f"Rate limit exceeded for IP: {client_ip}")
            return JSONResponse(
                status_code=429,
                content={
                    "error": "Too many requests. Please try again later.",
                    "retry_after": "60 seconds"
                }
            )
        
        # Add current request
        self.request_history[client_ip].append(now)
        
        # Start cleanup task if not running
        if not self.cleanup_task:
            self.cleanup_task = asyncio.create_task(self._cleanup_old_requests())
        
        return await call_next(request)
    
    async def _cleanup_old_requests(self):
        while True:
            await asyncio.sleep(60)  # Run every minute
            now = datetime.now()
            for ip in list(self.request_history.keys()):
                self.request_history[ip] = [
                    req_time for req_time in self.request_history[ip]
                    if now - req_time < timedelta(minutes=1)
                ]
                if not self.request_history[ip]:
                    del self.request_history[ip]

class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log processing time for endpoints
        if not request.url.path.endswith('/health'):
            logger.info(f"Processing time for {request.url.path}: {process_time:.3f}s")
        
        return response