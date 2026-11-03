from typing import Any, List, Optional
from pydantic import BaseModel, Field


class ErrorDetail(BaseModel):
    code: str = Field(..., description="Error code or categorization")
    message: str = Field(..., description="Human-readable error description")
    details: List[Any] = Field(default_factory=list, description="Additional context or validation details")


class StandardErrorResponse(BaseModel):
    error: ErrorDetail


class AppException(Exception):
    def __init__(
        self,
        status_code: int = 400,
        code: str = "BAD_REQUEST",
        message: str = "An error occurred.",
        details: Optional[List[Any]] = None,
    ):
        self.status_code = status_code
        self.code = code
        self.message = message
        self.details = details or []
        super().__init__(message)


class NotFoundException(AppException):
    def __init__(self, message: str = "Resource not found.", details: Optional[List[Any]] = None):
        super().__init__(status_code=404, code="NOT_FOUND", message=message, details=details)


class UnauthorizedException(AppException):
    def __init__(self, message: str = "Authentication required.", details: Optional[List[Any]] = None):
        super().__init__(status_code=401, code="UNAUTHORIZED", message=message, details=details)


class ForbiddenException(AppException):
    def __init__(self, message: str = "Access denied to requested resource.", details: Optional[List[Any]] = None):
        super().__init__(status_code=403, code="FORBIDDEN", message=message, details=details)


class ConflictException(AppException):
    def __init__(self, message: str = "Resource conflict.", details: Optional[List[Any]] = None):
        super().__init__(status_code=409, code="CONFLICT", message=message, details=details)


class ValidationException(AppException):
    def __init__(self, message: str = "Validation failed.", details: Optional[List[Any]] = None):
        super().__init__(status_code=422, code="VALIDATION_ERROR", message=message, details=details)

