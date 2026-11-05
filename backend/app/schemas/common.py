from datetime import datetime, timezone
from typing import Generic, TypeVar, List, Optional, Annotated, Any
from pydantic import BaseModel, Field, AfterValidator, PlainSerializer

DataT = TypeVar("DataT")


def ensure_utc_datetime(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, str):
        v = datetime.fromisoformat(v.replace("Z", "+00:00"))
    if isinstance(v, datetime):
        if v.tzinfo is None:
            return v.replace(tzinfo=timezone.utc)
        return v.astimezone(timezone.utc)
    return v


def serialize_utc_datetime(v: Any) -> Any:
    if v is None:
        return None
    if isinstance(v, datetime):
        if v.tzinfo is None:
            v = v.replace(tzinfo=timezone.utc)
        else:
            v = v.astimezone(timezone.utc)
        iso = v.isoformat()
        if iso.endswith("+00:00"):
            return iso[:-6] + "Z"
        if not iso.endswith("Z"):
            return iso + "Z"
        return iso
    return v


UTCDateTime = Annotated[
    datetime,
    AfterValidator(ensure_utc_datetime),
    PlainSerializer(serialize_utc_datetime, return_type=str, when_used="json"),
]


class ResponseEnvelope(BaseModel, Generic[DataT]):
    data: DataT
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    items: List[DataT]
    total: int = Field(..., ge=0)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1)

