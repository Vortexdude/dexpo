from typing import Optional, List
from pydantic import BaseModel


# https://stackoverflow.com/questions/67699451/make-every-field-as-optional-with-pydantic


class BaseClass(BaseModel):
    name: str
    state: str
    dry_run: Optional[bool] = True


class VpcModel(BaseClass):
    region: str
    cidr_block: str


class SecurityGroup(BaseClass):
    permissions: List
    description: str


class Subnet(BaseClass):
    cidr: str
    route_table: str


class InternetGatewayModel(BaseClass):
    pass


class RouteTableModel(BaseClass):
    DestinationCidrBlock: Optional[str] = None


class GlobalVpc(BaseModel):
    vpc: VpcModel
    route_tables: Optional[List[RouteTableModel]] = None
    internet_gateway: Optional[InternetGatewayModel] = None
    subnets: Optional[List[Subnet]] = None
    security_groups: Optional[List[SecurityGroup]] = None


class Ec2Model(BaseClass):
    instance_type: str
    ami: str
    subnet: str
    key_file: str
    region: str


class RootModel(BaseModel):
    vpcs: List[GlobalVpc]
    ec2: List = None
