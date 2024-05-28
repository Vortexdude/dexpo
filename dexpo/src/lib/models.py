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


class BucketLocation(BaseModel):
    Type: str
    Name: str


class BucketOptions(BaseModel):
    DataRedundancy: str
    Type: str


class CreateBucketConfiguration(BaseModel):
    LocationConstraint: str
    Location: Optional[BucketLocation] = None
    Bucket: Optional[BucketOptions] = None


class S3Model(BaseClass):
    ACL: str
    CreateBucketConfiguration: CreateBucketConfiguration
    GrantFullControl: Optional[str] = None
    GrantRead: Optional[str] = None
    GrantReadACP: Optional[str] = None
    GrantWrite: Optional[str] = None
    GrantWriteACP: Optional[str] = None
    ObjectLockEnabledForBucket: Optional[bool] = None
    ObjectOwnership: Optional[str] = None


class ConfigModel(BaseModel):
    vpcs: List[BaseVPC]
    ec2: List[Ec2Model]
    s3: List[S3Model]
