from pydantic import BaseModel
from typing import TypeVar, Generic, Optional, Dict, Any

T = TypeVar('T')

class HttpProcessInformation(BaseModel):
    method: str
    url: str
    client_host: Optional[str]
    user_agent: Optional[str]
    status: int
    latency_ms: str

class ExtraInformationLogger(BaseModel, Generic[T]):
    extra_data: Optional[T] = None

