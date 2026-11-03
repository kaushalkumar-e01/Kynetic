import logging
from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.core.errors import AppException

logger = logging.getLogger("kynetic.errors")


async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": exc.code,
                "message": exc.message,
                "details": exc.details,
            }
        },
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    details = []
    for error in exc.errors():
        loc = " -> ".join(str(part) for part in error.get("loc", []))
        msg = error.get("msg", "Validation error")
        details.append({"location": loc, "message": msg, "type": error.get("type", "value_error")})

    return JSONResponse(
        status_code=422,
        content={
            "error": {
                "code": "VALIDATION_ERROR",
                "message": "The request could not be processed due to invalid parameters.",
                "details": details,
            }
        },
    )


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> JSONResponse:
    code_map = {
        400: "BAD_REQUEST",
        401: "UNAUTHORIZED",
        403: "FORBIDDEN",
        404: "NOT_FOUND",
        405: "METHOD_NOT_ALLOWED",
        409: "CONFLICT",
        422: "UNPROCESSABLE_ENTITY",
        500: "INTERNAL_SERVER_ERROR",
    }
    code = code_map.get(exc.status_code, f"HTTP_{exc.status_code}")
    message = str(exc.detail) if exc.detail else "An HTTP error occurred."

    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": {
                "code": code,
                "message": message,
                "details": [],
            }
        },
    )


async def generic_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.exception(f"Unhandled server error on {request.method} {request.url.path}: {exc}")
    return JSONResponse(
        status_code=500,
        content={
            "error": {
                "code": "INTERNAL_SERVER_ERROR",
                "message": "An unexpected internal server error occurred.",
                "details": [],
            }
        },
    )

