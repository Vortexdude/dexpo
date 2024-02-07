from typing import Optional, List
from pydantic import BaseModel


# https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic


class BaseClass(BaseModel):
    name: str
    state: str
    dry_run: Optional[bool] = True


class SecurityGroup(BaseClass):
    permissions: List
    description: str


class Subnet(BaseClass):
    cidr: str


class InternetGatewayModel(BaseClass):
    pass


class RouteTableModel(BaseClass):
    DestinationCidrBlock: str


class VpcModel(BaseClass):
    region: str
    cidr_block: str
    route_table: Optional[RouteTableModel] = None
    internet_gateway: Optional[InternetGatewayModel] = None
    subnets: Optional[list[Subnet]] = None
    security_groups: Optional[List[SecurityGroup]] = None


class Ec2Model(BaseClass):
    instance_type: str
    ami: str
    subnet: str
    key_file: str
    region: str


class RootModel(BaseModel):
    vpc: List[VpcModel]
    ec2: List[Ec2Model]
