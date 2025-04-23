from fastapi import HTTPException, Request
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
import logging
from typing import Optional, Dict, Any

logger = logging.getLogger(__name__)

class KTPProcessingError(Exception):
    """Base exception for KTP processing errors."""
    def __init__(
        self,
        message: str,
        status_code: int = 500,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.status_code = status_code
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(KTPProcessingError):
    """Raised when input validation fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=422,
            details=details
        )

class OCRError(KTPProcessingError):
    """Raised when OCR processing fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )

class ModelError(KTPProcessingError):
    """Raised when ML model processing fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=500,
            details=details
        )

class DocumentError(KTPProcessingError):
    """Raised when document analysis fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )

class PreprocessingError(KTPProcessingError):
    """Raised when image preprocessing fails."""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(
            message=message,
            status_code=400,
            details=details
        )

class ErrorHandlingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        try:
            return await call_next(request)
        except KTPProcessingError as e:
            logger.error(f"KTP Processing error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": str(e)}
            )
        except HTTPException as e:
            logger.error(f"HTTP error: {str(e)}")
            return JSONResponse(
                status_code=e.status_code,
                content={"error": str(e.detail)}
            )
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            return JSONResponse(
                status_code=500,
                content={"error": "An unexpected error occurred"}
            )