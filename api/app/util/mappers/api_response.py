from typing import TypeVar, Generic, Optional
from pydantic import BaseModel

T = TypeVar('T')

class ApiResponse(BaseModel, Generic[T]):
    api_message: str
    api_data: Optional[T] = None
    errors: Optional[list[str]] = None
