"""These are docstrings basically a documentation of the module"""

import boto3
from botocore.exceptions import ClientError
from typing import Optional, List
from dexpo.manager import DexpoModule
from pydantic import BaseModel

REGION = 'ap-south-1'

extra_args = dict(
    resource_type='list',
)


class SecurityGroupPermissionIpRange(BaseModel):
    CidrIp: str
    Description: str


class SecurityGroupPermission(BaseModel):
    FromPort: int
    ToPort: int
    IpProtocol: str
    IpRanges: List[SecurityGroupPermissionIpRange]


class SecurityGroupInput(BaseModel):
    name: str
    deploy: bool
    description: str
    permissions: list[SecurityGroupPermission]


module = DexpoModule(
    base_arg=SecurityGroupInput,
    extra_args=extra_args,
    module_type='security_groups'
)
logger = module.logger


class SecurityGroupManager:
    def __init__(self, sb_input: SecurityGroupInput):
        self.sb_input = sb_input
        self.ec2_client = boto3.client("ec2")
        self.ec2_resource = boto3.resource('ec2')

    def validate(self) -> dict:
        response = self.ec2_client.describe_subnets(
            Filters=[
                {
                    'Name': "tag:Name",
                    'Values': [
                        self.sb_input.name,
                    ],
                },
            ],
        )
        if not response['Subnets']:
            logger.info("No subnets found in the cloud")
            return {}

        return response['Subnets'][0]

    def create(self, vpc_resource, rt_resource):
        if self.sb_input.deploy:
            try:
                subnet = vpc_resource.create_subnet(
                    CidrBlock=self.sb_input.cidr,
                    AvailabilityZone=f"{self.sb_input.region}{self.sb_input.zone}"
                )

                subnet.create_tags(
                    Tags=[{
                        "Key": "Name",
                        "Value": self.sb_input.name
                    }]
                )

                rt_resource.associate_with_subnet(SubnetId=subnet.id)
                logger.info(f"Subnet {self.sb_input.name} created successfully!")
                return subnet.id

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    logger.warning(f"Subnet {self.sb_input.name} already exist")


def _validate_security_group(rt: SecurityGroupManager, index):
    print(f"Validating SecurityGroup {index}........")


def _create_security_group(rt: SecurityGroupManager, index):
    print(f"Creating SecurityGroup {index}........")


def _delete_security_group(rt: SecurityGroupManager, index):
    print(f"deleting SecurityGroup {index}........")


def run_module(action: str, data: dict, *args, **kwargs):
    inp = SecurityGroupInput(**data)
    rt = SecurityGroupManager(inp)

    if action == 'validate':
        return _validate_security_group(rt, index=kwargs['index'])

    elif action == 'create':
        return _create_security_group(rt, index=kwargs['index'])

    elif action == 'delete':
        return _delete_security_group(rt, index=kwargs['index'])
