"""These are docstrings basically a documentation of the module"""

import boto3
from .test import DexpoModule
from pydantic import BaseModel

result = dict(
    changed=False,
    vpc=dict()
)


class VpcInput(BaseModel):
    name: str
    deploy: bool
    dry_run: bool
    region: str
    CidrBlock: str


module = DexpoModule(
    base_arg=VpcInput,
    extra_args=None,
    module_type='vpc'
)
logger = module.logger


class VpcManager:
    def __init__(self, vpc_input: VpcInput):
        self.vpc_input = vpc_input
        self.ec2_client = boto3.client("ec2", region_name=self.vpc_input.region)
        self.ec2_resource = boto3.resource('ec2', region_name=self.vpc_input.region)

    def _wait_until_available(self, resource):
        """Wait until the resource is available."""

        resource.wait_until_available()
        logger.info(f"{self.vpc_input.name} is available.")

    def create(self) -> dict:
        """launch the vpc if the vpc not available"""
        if self.vpc_input.deploy:
            response = self.ec2_client.create_vpc(CidrBlock=self.vpc_input.CidrBlock)
            vpc_resource = self.ec2_resource.Vpc(response['Vpc']['VpcId'])
            self._wait_until_available(vpc_resource)
            vpc_resource.create_tags(
                Tags=[{
                    "Key": "Name",
                    "Value": self.vpc_input.name
                }]
            )  # adding name to the VPC

            return response
        else:
            return {}

    def validate(self) -> dict:
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""
        filters = []
        if self.vpc_input.CidrBlock:
            filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.vpc_input.CidrBlock]
            })

        elif self.vpc_input.name:
            filters.append({
                "Name": "tag:Name",
                "Values": [self.vpc_input.name]

            })
        else:
            return {'message': "For search the vpc need to give Identification"}

        response = self.ec2_client.describe_vpcs(Filters=filters)
        if not response['Vpcs']:
            return {}

        return response['Vpcs'][0]

    def delete(self):
        pass


def _validate_vpc(vpc: VpcManager):
    response = vpc.validate()
    module.save_state(response)
    if not response:
        module.logger.debug(
            f"No Vpc found under the name {vpc.vpc_input.name} and CIDR block {vpc.vpc_input.CidrBlock}")

    return response


def _create_vpc(vpc: VpcManager):
    response = vpc.create()
    if response:
        module.save_state(response['Vpc'])
        logger.info(f"{vpc.vpc_input.name} VPC Created Successfully!")
    else:
        logger.warn(f"Could not able to create VPC {vpc.vpc_input.name}")
    return response


def _delete_vpc(vpc_name: str):
    pass


def run_module(action: str, data: dict):
    inp = VpcInput(**data)
    vpc = VpcManager(inp)
    module.base_args = vpc.vpc_input
    if action == 'validate':
        return _validate_vpc(vpc)

    elif action == 'create':
        return _create_vpc(vpc)

    elif action == 'delete':
        return _delete_vpc(vpc_name="nothing")
