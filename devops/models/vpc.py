from pydantic import BaseModel
from typing import Optional


class ResourceValidationResponseModel(BaseModel):
    available: bool
    id: Optional[str]


class ResourceCreationResponseModel(BaseModel):
    status: bool
    message: str
    resource_id: Optional[str]
