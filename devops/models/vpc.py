from pydantic import BaseModel
from typing import Optional, Any


class ResourceValidationResponseModel(BaseModel):
    available: bool
    id: Optional[str]
    resource: Optional[Any]
    message: str


class ResourceCreationResponseModel(BaseModel):
    status: bool
    message: str
    resource_id: Optional[str]
    resource: Optional[Any]
