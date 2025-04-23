from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .core.config import get_settings
from .core.middleware import RateLimitMiddleware, ProcessingTimeMiddleware
from .core.errors import ErrorHandlingMiddleware
from .api.routes import router

settings = get_settings()

def create_application() -> FastAPI:
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="KTP Recognition API for processing Indonesian ID cards",
        version="1.0.0",
        openapi_url=f"{settings.API_V1_STR}/openapi.json",
        docs_url=f"{settings.API_V1_STR}/docs",
        redoc_url=f"{settings.API_V1_STR}/redoc"
    )

    # Set up CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Add custom middleware
    app.add_middleware(RateLimitMiddleware)
    app.add_middleware(ProcessingTimeMiddleware)
    app.add_middleware(ErrorHandlingMiddleware)

    # Include API routes
    app.include_router(router, prefix=settings.API_V1_STR)

    @app.get("/")
    async def root():
        """Root endpoint that redirects to API documentation."""
        return {
            "message": "Welcome to KTP Recognition API",
            "documentation": f"{settings.API_V1_STR}/docs"
        }

    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy"}

    return app

app = create_application()