"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from pydantic import BaseModel, ValidationError
from typing import Optional

result = dict(
    changed=False,
    ig=dict()
)


class InternetGatewayInput(BaseModel):
    name: str
    deploy: bool
    dry_run: bool = True
    region: Optional[str | None] = 'ap-south-1'


module = DexpoModule(
    base_arg=InternetGatewayInput,
    extra_args=None,
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
            module.logger.info(f"Internet Gateway {self.ig_input.name} Created Successfully!")
            ig_id = response['InternetGateway']['InternetGatewayId']
            if vpc_id:
                self.ec2_resource.Vpc(vpc_id).attach_internet_gateway(InternetGatewayId=ig_id)
                module.logger.info(f"Internet Gateway {self.ig_input.name} attached to vpc {ig_id} Successfully!")

        return response

    def validate(self) -> dict:
        response = self.ec2_client.describe_internet_gateways(Filters=[{
            "Name": "tag:Name",
            "Values": [self.ig_input.name]
        }])
        if not response['InternetGateways']:
            return {}

        return response['InternetGateways'][0]

    def delete(self):
        pass


def _get_vpc_id(ig_name, state) -> str:
    for vpc_entry in state.get("vpcs", []):
        if vpc_entry.get("internet_gateway", {}).get("name") == ig_name:
            return vpc_entry.get("vpc", {}).get("VpcId")


def _validate_ig(ig: InternetGatewayManager):
    response = ig.validate()
    if not response:
        module.logger.debug(f"No internet gateway found under name {ig.ig_input.name}")
    else:
        module.save_state(response)

    return response


def _create_ig(ig: InternetGatewayManager):
    state = module.get_state()
    vpc_id = _get_vpc_id(ig.ig_input.name, state)
    response = ig.create(vpc_id)
    if not response:
        logger.info(f"There is an Error while creating internet gateway.")
    else:
        module.save_state(response['InternetGateway'])

    return response


def run_module(action: str, data: dict, **kwargs):
    inp = InternetGatewayInput(**data)
    ig = InternetGatewayManager(inp)
    module.base_args = ig.ig_input
    if action == 'validate':
        return _validate_ig(ig)

    if action == 'create':
        return _create_ig(ig)

    if action == 'delete':
        ig.delete()
