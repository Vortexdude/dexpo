from typing import Optional, List
from pydantic import BaseModel

# https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic


class BaseClass(BaseModel):
    name: str
    state: str
    dry_run: Optional[bool] = True


class InternetGatewayModel(BaseClass):
    pass


class RouteTableModel(BaseClass):
    DestinationCidrBlock: str


class VpcModel(BaseClass):
    region: str
    cidr_block: str
    route_table: Optional[RouteTableModel] = None
    internet_gateway: Optional[InternetGatewayModel] = None


class RootModel(BaseModel):
    vpc: List[VpcModel]
    ec2: Optional[List] = None

