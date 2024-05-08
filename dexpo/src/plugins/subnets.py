"""These are docstrings basically a documentation of the module"""

import boto3
from botocore.exceptions import ClientError

from dexpo.manager import DexpoModule
from pydantic import BaseModel


REGION = 'ap-south-1'

extra_args = dict(
    resource_type='list',
)


class SubnetsInput(BaseModel):
    name: str
    deploy: bool
    cidr: str
    zone: str
    route_table: str


module = DexpoModule(
    base_arg=SubnetsInput,
    extra_args=None,
    module_type='subnets'
)
logger = module.logger


class SubnetManager:
    def __init__(self, sb_input: SubnetsInput):
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


def _validate_subnets(rt: SubnetManager, index):
    print(f"Validating Subnets {index}........")


def _create_subnets(rt: SubnetManager, index):
    print(f"Creating Subnets {index}........")


def _delete_subnets(rt: SubnetManager, index):
    print(f"deleting Subnets {index}........")


def run_module(action: str, data: dict, *args, **kwargs):
    inp = SubnetsInput(**data)
    rt = SubnetManager(inp)

    if action == 'validate':
        return _validate_subnets(rt, index=kwargs['index'])

    elif action == 'create':
        return _create_subnets(rt, index=kwargs['index'])

    elif action == 'delete':
        return _delete_subnets(rt, index=kwargs['index'])
