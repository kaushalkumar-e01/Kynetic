from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.v1.router import api_router
from app.core.config import settings
from app.core.errors import AppException
from app.core.exception_handlers import (
    app_exception_handler,
    validation_exception_handler,
    http_exception_handler,
    generic_exception_handler,
)
from app.api.v1.endpoints.health import get_health


def create_app() -> FastAPI:
    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Backend API service for Kynetic — Knowledge in Motion",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
    )

    # Configure CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors_origins_list,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register Exception Handlers
    app.add_exception_handler(AppException, app_exception_handler)
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(StarletteHTTPException, http_exception_handler)
    app.add_exception_handler(Exception, generic_exception_handler)

    # Include API Routers
    app.include_router(api_router, prefix=settings.API_V1_PREFIX)

    # Root health check endpoint for standard platform load balancers
    app.add_api_route("/health", get_health, methods=["GET"], tags=["Health"], include_in_schema=False)

    @app.get("/", tags=["Root"], include_in_schema=False)
    def root():
        return {
            "name": settings.APP_NAME,
            "version": "0.1.0",
            "docs": "/docs",
            "health": f"{settings.API_V1_PREFIX}/health",
        }

    return app


app = create_app()

