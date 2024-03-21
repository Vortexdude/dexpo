from pydantic import BaseModel
from typing import Optional, Any
from devops.models.config import VpcModel, InternetGatewayModel, Subnet, SecurityGroup, RouteTableModel


class ResourceValidationResponseModel(BaseModel):
    available: bool
    id: Optional[str] | Optional[list]
    resource: Optional[Any] | Optional[list]
    properties: VpcModel | InternetGatewayModel | Subnet | SecurityGroup | RouteTableModel
    type: str


class ResourceCreationResponseModel(BaseModel):
    status: bool
    message: str
    resource_id: Optional[str]
    resource: Optional[Any]


class DeleteResourceResponseModel(BaseModel):
    status: bool
    resource: str
    message: str
