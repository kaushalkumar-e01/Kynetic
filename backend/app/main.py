import os
import logging
from contextlib import asynccontextmanager
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

logger = logging.getLogger("kynetic.startup")


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Ensure local storage directories exist automatically
    os.makedirs(settings.STORAGE_LOCAL_DIR, exist_ok=True)

    # 2. In development or test, ensure database tables exist and seed initial bank if fresh
    if settings.APP_ENV in ("development", "test"):
        try:
            import app.models  # Ensure all SQLAlchemy models are registered to Base.metadata
            from app.models import Base
            from app.db.session import engine, SessionLocal
            Base.metadata.create_all(bind=engine)

            with SessionLocal() as db:
                from app.services.assessment_service import assessment_service
                assessment_service.seed_initial_bank_if_empty(db)
        except Exception as e:
            logger.warning("Startup database auto-initialization notice: %s", str(e))

    yield


def create_app() -> FastAPI:
    # Fail fast if APP_ENV is not development/test and SECRET_KEY is still insecure default
    default_insecure = "insecure-development-secret-key-replace-in-production"
    if settings.APP_ENV not in ("development", "test") and settings.SECRET_KEY == default_insecure:
        error_msg = f"FATAL: Insecure default SECRET_KEY cannot be used when APP_ENV is '{settings.APP_ENV}'."
        logger.critical(error_msg)
        raise RuntimeError(error_msg)

    app = FastAPI(
        title=f"{settings.APP_NAME} API",
        description="Backend API service for Kynetic — Knowledge in Motion",
        version="0.1.0",
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url=f"{settings.API_V1_PREFIX}/openapi.json",
        lifespan=lifespan,
    )

    # Configure CORS with local multi-port and LAN dev compatibility
    cors_kwargs = {
        "allow_origins": settings.cors_origins_list,
        "allow_credentials": True,
        "allow_methods": ["*"],
        "allow_headers": ["*"],
    }
    if settings.APP_ENV == "development":
        cors_kwargs["allow_origin_regex"] = r"^https?://(localhost|127\.0\.0\.1|0\.0\.0\.0|192\.168\.\d+\.\d+|10\.\d+\.\d+\.\d+|172\.(1[6-9]|2\d|3[01])\.\d+\.\d+)(:\d+)?$"

    app.add_middleware(CORSMiddleware, **cors_kwargs)

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
