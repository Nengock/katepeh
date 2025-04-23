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
    def __init__(self, app, requests_per_minute: int = 60):
        super().__init__(app)
        self.requests_per_minute = requests_per_minute
        self.request_history = defaultdict(list)
        self.cleanup_task = None
        
    async def dispatch(self, request: Request, call_next):
        # Get client IP, preferring X-Forwarded-For header for proxy support
        client_ip = request.headers.get("X-Forwarded-For", request.client.host)
        if isinstance(client_ip, str) and "," in client_ip:
            client_ip = client_ip.split(",")[0].strip()
            
        now = datetime.now()
        
        # Skip rate limiting for health check and test endpoints
        if request.url.path == '/health' or request.url.path.startswith('/test'):
            return await call_next(request)
        
        # Clean old requests before checking limits
        try:
            self.request_history[client_ip] = [
                req_time for req_time in self.request_history[client_ip]
                if isinstance(req_time, datetime) and (now - req_time).total_seconds() < 60
            ]
            
            # Check rate limit
            if len(self.request_history[client_ip]) >= self.requests_per_minute:
                logger.warning(f"Rate limit exceeded for IP: {client_ip}")
                return JSONResponse(
                    status_code=429,
                    content={
                        "error": "Too many requests. Please try again later.",
                        "detail": "Too many requests. Please try again later.",
                        "retry_after": "60 seconds"
                    }
                )
            
            # Add current request
            self.request_history[client_ip].append(now)
            
            # Start cleanup task if not running
            if not self.cleanup_task or self.cleanup_task.done():
                self.cleanup_task = asyncio.create_task(self._cleanup_old_requests())
                
        except Exception as e:
            logger.error(f"Error in rate limiting: {str(e)}")
            # On error, allow the request through
            return await call_next(request)
        
        return await call_next(request)
    
    async def _cleanup_old_requests(self):
        """Clean up old request records periodically."""
        try:
            while True:
                await asyncio.sleep(60)  # Run every minute
                now = datetime.now()
                
                # Use list() to avoid runtime modification errors
                for ip in list(self.request_history.keys()):
                    try:
                        self.request_history[ip] = [
                            req_time for req_time in self.request_history[ip]
                            if isinstance(req_time, datetime) and (now - req_time).total_seconds() < 60
                        ]
                        if not self.request_history[ip]:
                            del self.request_history[ip]
                    except Exception as e:
                        logger.error(f"Error cleaning up requests for IP {ip}: {str(e)}")
                        continue
        except asyncio.CancelledError:
            # Handle task cancellation gracefully
            pass
        except Exception as e:
            logger.error(f"Error in cleanup task: {str(e)}")

class ProcessingTimeMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = datetime.now()
        response = await call_next(request)
        process_time = (datetime.now() - start_time).total_seconds()
        
        response.headers["X-Process-Time"] = str(process_time)
        
        # Log processing time for endpoints except health checks
        if not request.url.path == '/health':
            logger.info(f"Processing time for {request.url.path}: {process_time:.3f}s")
        
        return response