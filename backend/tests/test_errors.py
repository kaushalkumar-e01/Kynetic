from app.core.errors import (
    NotFoundException,
    UnauthorizedException,
    ForbiddenException,
    ConflictException,
    ValidationException,
    StandardErrorResponse,
)


def test_app_exceptions():
    nf = NotFoundException("User not found.")
    assert nf.status_code == 404
    assert nf.code == "NOT_FOUND"
    assert nf.message == "User not found."
    assert nf.details == []

    unauth = UnauthorizedException("Token expired.")
    assert unauth.status_code == 401
    assert unauth.code == "UNAUTHORIZED"

    forb = ForbiddenException("Access forbidden.")
    assert forb.status_code == 403
    assert forb.code == "FORBIDDEN"

    conf = ConflictException("Email already exists.")
    assert conf.status_code == 409
    assert conf.code == "CONFLICT"

    val = ValidationException("Invalid fields.", details=[{"field": "email", "issue": "malformed"}])
    assert val.status_code == 422
    assert val.code == "VALIDATION_ERROR"
    assert len(val.details) == 1


def test_standard_error_schema():
    payload = {
        "error": {
            "code": "VALIDATION_ERROR",
            "message": "The request could not be processed.",
            "details": [{"location": "body -> email", "message": "Field required"}],
        }
    }
    obj = StandardErrorResponse(**payload)
    assert obj.error.code == "VALIDATION_ERROR"
    assert obj.error.message == "The request could not be processed."
    assert len(obj.error.details) == 1
