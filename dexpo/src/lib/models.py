from pydantic import BaseModel
from typing import List, Optional


class BaseClass(BaseModel):
    name: str
    deploy: bool


class Vpc(BaseClass):
    dry_run: bool
    region: str
    CidrBlock: str


class RouteTable(BaseClass):
    DestinationCidrBlock: Optional[str] = None


class InternetGateway(BaseClass):
    pass


class Subnet(BaseClass):
    cidr: str
    zone: str
    route_table: str


class SecurityGroupPermissionIpRange(BaseModel):
    CidrIp: str
    Description: str


class SecurityGroupPermission(BaseModel):
    FromPort: int
    ToPort: int
    IpProtocol: str
    IpRanges: List[SecurityGroupPermissionIpRange]


class SecurityGroup(BaseClass):
    description: str
    permissions: list[SecurityGroupPermission]


class BaseVPC(BaseModel):
    vpc: Vpc
    route_tables: List[RouteTable]
    internet_gateway: InternetGateway
    subnets: List[Subnet]
    security_groups: List[SecurityGroup]


class Ec2Model(BaseClass):
    instance_type: str
    ami: str
    subnet: str
    key_file: str
    region: str
    subnet: str
    vpc: str
    security_groups: Optional[list] = None


class ConfigModel(BaseModel):
    vpcs: List[BaseVPC]
    ec2: List[Ec2Model]
