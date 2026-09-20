"""Shared response envelope schemas.

Will define standard success and error response wrappers used across
endpoints, for example { "data": ..., "meta": { "request_id": "..." } }.
"""
from typing import Generic, Optional, TypeVar
from pydantic import BaseModel, Field

T = TypeVar("T")

class Meta(BaseModel):
    request_id: Optional[str] = None

class ErrorDetail(BaseModel):
    code: str
    message: str

class SuccessResponse(BaseModel, Generic[T]):
    data: T
    meta: Meta = Field(default_factory=Meta)

class ErrorResponse(BaseModel):
    error: ErrorDetail
    meta: Meta = Field(default_factory=Meta)
