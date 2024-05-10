"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from pydantic import BaseModel, ValidationError
from typing import Optional

extra_args = dict(
    resource_type='dict',
)


class InternetGatewayInput(BaseModel):
    name: str
    deploy: bool
    dry_run: bool = True
    region: Optional[str | None] = 'ap-south-1'


module = DexpoModule(
    base_arg=InternetGatewayInput,
    extra_args=extra_args,
    module_type='internet_gateway'
)

logger = module.logger


class InternetGatewayManager:
    def __init__(self, ig_input: InternetGatewayInput):
        self.ig_input = ig_input
        self.ec2_client = boto3.client("ec2", region_name=self.ig_input.region)
        self.ec2_resource = boto3.resource('ec2', region_name=self.ig_input.region)

    def create(self, vpc_id) -> dict:
        """launch the vpc if the vpc not available"""
        response = self.ec2_client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.ig_input.name
                }]
            }]
        )

        if response['InternetGateway']:
            logger.info(f"Internet Gateway {self.ig_input.name} Created Successfully!")
            ig_id = response['InternetGateway']['InternetGatewayId']
            if vpc_id:
                self.ec2_resource.Vpc(vpc_id).attach_internet_gateway(InternetGatewayId=ig_id)
                logger.info(f"Internet Gateway {self.ig_input.name} attached to vpc {vpc_id} Successfully!")

        return response['InternetGateway']

    def validate(self) -> dict:
        response = self.ec2_client.describe_internet_gateways(Filters=[{
            "Name": "tag:Name",
            "Values": [self.ig_input.name]
        }])
        if not response['InternetGateways']:
            return {}

        return response['InternetGateways'][0]

    @staticmethod
    def delete(vpc_resource, vpc_id):
        internet_gateways = vpc_resource.internet_gateways.all()
        if internet_gateways:
            for internet_gateway in internet_gateways:
                logger.info(f"Detaching and Removing igw-id {internet_gateway.id}")
                internet_gateway.detach_from_vpc(VpcId=vpc_id)
                internet_gateway.delete()  # dry_run=True
                logger.info("Internet Gateway Deleted Successfully")


def _get_vpc_id(ig_name, state) -> str:
    for vpc_entry in state.get("vpcs", []):
        if vpc_entry.get("internet_gateway", {}).get("name") == ig_name:
            return vpc_entry.get("vpc", {}).get("VpcId")


def _validate_ig(ig: InternetGatewayManager):
    logger.debug("Validating Internet Gateway.......")
    response = ig.validate()
    if module.validate_resource('InternetGatewayId', response):
        return

    module.save_state(response)


def _create_ig(ig: InternetGatewayManager):
    logger.debug("creating Internet Gateway...")
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        if vpc_entry.get('internet_gateway', {}).get('InternetGatewayId'):
            logger.info('InternetGateway already exist')
            return

    vpc_id = _get_vpc_id(ig.ig_input.name, _current_state)
    response = ig.create(vpc_id)
    if not response:
        logger.info(f"There is an Error while creating internet gateway.")
    else:
        module.save_state(response)

    return response


def _delete_ig(ig: InternetGatewayManager):
    logger.debug("Deleting Internet Gateway...")
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        if vpc_entry.get('internet_gateway', {}).get('InternetGatewayId'):
            vpc_id = module.get_resource_values('internet_gateway', ig.ig_input.name, 'VpcId')
            vpc_resource = boto3.resource('ec2').Vpc(vpc_id)
            ig.delete(vpc_resource, vpc_id)
            module.update_state(data=ig.ig_input.model_dump())
        else:
            logger.warn("InternetGateway is Not Launched Yet...")


def run_module(action: str, data: dict, **kwargs):
    inp = InternetGatewayInput(**data)
    ig = InternetGatewayManager(inp)
    module.base_args = ig.ig_input
    if action == 'validate':
        return _validate_ig(ig)

    if action == 'create':
        return _create_ig(ig)

    if action == 'delete':
        return _delete_ig(ig)
