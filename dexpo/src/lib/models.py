from pydantic import BaseModel
from typing import List, Optional


class Vpc(BaseModel):
    name: str
    state: str
    dry_run: bool
    region: str
    cidr_block: str


class RouteTable(BaseModel):
    name: str
    state: str
    DestinationCidrBlock: Optional[str] = None


class InternetGateway(BaseModel):
    name: str
    state: str


class Subnet(BaseModel):
    name: str
    state: str
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


class SecurityGroup(BaseModel):
    name: str
    description: str
    state: str
    permissions: list[SecurityGroupPermission]


class BaseVPC(BaseModel):
    vpc: Vpc
    route_tables: List[RouteTable]
    internet_gateway: InternetGateway
    subnets: List[Subnet]
    security_groups: List[SecurityGroup]


class ConfigModel(BaseModel):
    vpcs: List[BaseVPC]
    ec2: List
