"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from pydantic import BaseModel

extra_args = dict(
    resource_type='dict',
)


class VpcInput(BaseModel):
    name: str
    deploy: bool
    dry_run: bool
    region: str
    CidrBlock: str


module = DexpoModule(
    base_arg=VpcInput,
    extra_args=extra_args,
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

            return response['Vpc']
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
            logger.error('For search the vpc need to give Identification')
            return {}

        response = self.ec2_client.describe_vpcs(Filters=filters)
        if not response['Vpcs']:
            return {}

        return response['Vpcs'][0]

    def delete(self, vpc_id):
        """ Delete the VPC """
        try:
            self.ec2_client.delete_vpc(VpcId=vpc_id)
            logger.info("VPC Deleted Successfully!")
        except Exception as e:
            logger.error("Cant able to delete the VPC")
            raise Exception("cant able to delete VPC")


def _validate_vpc(vpc: VpcManager) -> None:
    logger.debug("Validating VPC........")
    response = vpc.validate()
    if module.validate_resource('VpcId', response):
        return

    module.save_state(response)


def _create_vpc(vpc: VpcManager) -> None:
    logger.debug("Creating VPC........")
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        if vpc_entry.get('vpc', {}).get('VpcId'):
            logger.info('Vpc already exist')
            return

    response = vpc.create()
    if response:
        module.save_state(response)
        logger.info(f"{vpc.vpc_input.name} VPC Created Successfully!")
    else:
        logger.warn(f"Could not able to create VPC {vpc.vpc_input.name}")


def _delete_vpc(vpc: VpcManager):
    _current_state = module.get_state()
    for global_vpc in _current_state.get('vpcs', []):
        if 'vpc' not in global_vpc and not global_vpc.get('vpc', {}).get('VpcId'):
            logger.error("cant able to find vpc in state")
            return
        vpc_id = global_vpc.get('vpc', {}).get('VpcId')
        vpc.delete(vpc_id)
        module.save_state(data=vpc.vpc_input.model_dump())


def run_module(action: str, data: dict):
    inp = VpcInput(**data)
    vpc = VpcManager(inp)
    module.base_args = vpc.vpc_input
    if action == 'validate':
        return _validate_vpc(vpc)

    elif action == 'create':
        return _create_vpc(vpc)

    elif action == 'delete':
        return _delete_vpc(vpc)
