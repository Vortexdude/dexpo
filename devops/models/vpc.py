from pydantic import BaseModel
from typing import Optional, Any


class ResourceValidationResponseModel(BaseModel):
    available: bool
    id: Optional[str] | Optional[list]
    resource: Optional[Any] | Optional[list]
    message: str


class ResourceCreationResponseModel(BaseModel):
    status: bool
    message: str
    resource_id: Optional[str]
    resource: Optional[Any]
