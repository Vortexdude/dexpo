from typing import List, Optional
from pydantic import BaseModel
from dexpo.src.lib.model import Vpc as BaseVpc
from dexpo.src.lib.model import SecurityGroup as BaseSecurityGroup
from dexpo.src.lib.model import Subnet as BaseSubnet
from dexpo.src.lib.model import RouteTable as BaseRouteTable
from dexpo.src.lib.model import InternetGateway as BaseInternetGateway


class CidrBlockState(BaseModel):
    State: Optional[str]


class CidrBlockAssociation(BaseModel):
    AssociationId: Optional[str]
    CidrBlock: Optional[str]
    CidrBlockState: CidrBlockState


class Tag(BaseModel):
    Key: Optional[str]
    Value: Optional[str]


class Vpc(BaseVpc):
    DhcpOptionsId: Optional[str]
    State: Optional[str]
    VpcId: Optional[str]
    OwnerId: Optional[str]
    InstanceTenancy: Optional[str]
    CidrBlockAssociationSet: Optional[List[CidrBlockAssociation]]
    IsDefault: Optional[bool]
    Tags: Optional[List[Tag]]


class AssociationState(BaseModel):
    State: str


class RouteAssociation(BaseModel):
    Main: bool
    RouteTableAssociationId: str
    RouteTableId: str
    SubnetId: str
    AssociationState: AssociationState


class Route(BaseModel):
    DestinationCidrBlock: str
    GatewayId: str
    Origin: str
    State: str


class RouteTable(BaseRouteTable):
    Associations: Optional[List[RouteAssociation]]
    PropagatingVgws: Optional[List[str]]
    RouteTableId: Optional[str]
    Routes: Optional[List[Route]]
    Tags: Optional[List[Tag]]
    VpcId: Optional[str]
    OwnerId: Optional[str]


class Attachment(BaseModel):
    State: str
    VpcId: str


class InternetGateway(BaseInternetGateway):
    Attachments: Optional[List[Attachment]]
    InternetGatewayId: Optional[str]
    OwnerId: Optional[str]
    Tags: Optional[List[Tag]]


class Subnet(BaseSubnet):
    AvailabilityZone: Optional[str]
    AvailabilityZoneId: Optional[str]
    AvailableIpAddressCount: int
    CidrBlock: Optional[str]
    DefaultForAz: Optional[bool]
    MapPublicIpOnLaunch: Optional[bool]
    MapCustomerOwnedIpOnLaunch: Optional[bool]
    State: Optional[str]
    SubnetId: Optional[str]
    VpcId: Optional[str]
    OwnerId: Optional[str]
    AssignIpv6AddressOnCreation: Optional[bool]
    Ipv6CidrBlockAssociationSet: List[str]
    Tags: List[Tag]
    SubnetArn: Optional[str]
    EnableDns64: Optional[bool]
    Ipv6Native: Optional[bool]
    PrivateDnsNameOptionsOnLaunch: dict


class Permission(BaseModel):
    FromPort: int
    ToPort: int
    IpProtocol: str
    IpRanges: List[dict]


class SecurityGroup(BaseSecurityGroup):
    Description: Optional[str]
    GroupName: Optional[str]
    IpPermissions: Optional[List[Permission]]
    OwnerId: Optional[str]
    GroupId: Optional[str]
    IpPermissionsEgress: Optional[List[Permission]]
    Tags: Optional[List[Tag]]
    VpcId: Optional[str]


class BaseVPC(BaseModel):
    vpc: Vpc
    internet_gateway: InternetGateway
    route_tables: List[RouteTable]
    subnets: List[Subnet]
    security_groups: List[SecurityGroup]


class VpcState(BaseModel):
    vpcs: List[BaseVPC]
    # ec2: List

# You can use these models like so:
