"""These are docstrings basically a documentation of the module"""
from dexpo.settings import trace_route
import boto3
from dexpo.manager import DexpoModule
from dexpo.src.exceptions.main import KeyMissingException, Boto3OperationError
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
    SERVICE = 'ec2'

    def __init__(self, vpc_input: VpcInput):
        self.vpc_input = vpc_input
        self.ec2_client = boto3.client(self.SERVICE, region_name=self.vpc_input.region)
        self.ec2_resource = boto3.resource(self.SERVICE, region_name=self.vpc_input.region)

    def _wait_until_available(self, resource):
        """Wait until the resource is available."""

        resource.wait_until_available()
        logger.info(f"{self.vpc_input.name} is available.")

    def create(self) -> dict:
        """launch the vpc if the vpc not available"""
        if not self.vpc_input.deploy:
            raise KeyMissingException('deploy', 'vpc')

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

    def validate(self) -> dict:
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""
        filters = []
        if not self.vpc_input.CidrBlock:
            raise KeyMissingException('CidrBlock', 'vpc')

        if not self.vpc_input.name:
            raise KeyMissingException('CidrBlock', 'vpc')

        filters.append({
            'Name': 'cidr-block-association.cidr-block',
            'Values': [self.vpc_input.CidrBlock]
        })

        filters.append({
            "Name": "tag:Name",
            "Values": [self.vpc_input.name]

        })

        response = self.ec2_client.describe_vpcs(Filters=filters)
        if not response['Vpcs']:
            return {}

        return response['Vpcs'][0]

    def delete(self, vpc_id):
        """ Delete the VPC """
        response = self.ec2_client.delete_vpc(VpcId=vpc_id)
        if response:
            logger.info("VPC Deleted Successfully!")
        else:
            logger.error("Cant able to delete the VPC")
            raise Boto3OperationError()


def _validate_vpc(vpc: VpcManager) -> None:
    logger.debug("Validating VPC........")
    response = vpc.validate()
    if not response:  # if the vpc not exist in the cloud
        _current_state = module.get_state()
        for global_vpc in _current_state.get('vpcs', []):
            # check the input name and the state name
            if global_vpc.get('vpc').get('name') == vpc.vpc_input.name:
                vpc_id = global_vpc.get('vpc').get('VpcId', '')
                # if the vpc exist in state
                if vpc_id:
                    logger.warning("VPC exists in the state not in cloud")
                    logger.info("fixing issue . . . ")
                    module.update_state(vpc.vpc_input.model_dump())
                    return

    else:
        module.save_state(response)


def _create_vpc(vpc: VpcManager) -> None:
    logger.debug("Creating VPC........")
    state_container = module.get_state()
    for vpc_entry in state_container.get('vpcs', []):
        if vpc_entry.get('vpc', {}).get('name') == vpc.vpc_input.name:
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
    logger.debug("Deleting VPC...")
    state_container = module.get_state()
    for vpc_entry in state_container.get('vpcs', []):
        if vpc_entry.get('vpc', {}).get('VpcId'):
            vpc_id = vpc_entry.get('vpc', {}).get('VpcId')
            vpc.delete(vpc_id)
            module.update_state(data=vpc.vpc_input.model_dump())
        else:
            logger.warn("VPC is Not Launched Yet...")


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
