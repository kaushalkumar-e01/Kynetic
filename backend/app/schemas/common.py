from typing import Generic, TypeVar, List, Optional
from pydantic import BaseModel, Field

DataT = TypeVar("DataT")


class ResponseEnvelope(BaseModel, Generic[DataT]):
    data: DataT
    message: Optional[str] = None


class PaginatedResponse(BaseModel, Generic[DataT]):
    items: List[DataT]
    total: int = Field(..., ge=0)
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1)

