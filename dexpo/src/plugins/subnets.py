"""These are docstrings basically a documentation of the module"""

import boto3
from botocore.exceptions import ClientError
from dexpo.src.lib.models import Subnet
from dexpo.manager import DexpoModule

REGION = 'ap-south-1'

extra_args = dict(
    resource_type='list',
)


class SubnetsInput(Subnet):
    pass


module = DexpoModule(
    base_arg=SubnetsInput,
    extra_args=extra_args,
    module_type='subnets'
)
logger = module.logger


class SubnetManager:
    SERVICE = 'ec2'

    def __init__(self, sb_input: SubnetsInput):
        self.sb_input = sb_input
        self.ec2_client = boto3.client(self.SERVICE)
        self.ec2_resource = boto3.resource(self.SERVICE)

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
            return {}

        return response['Subnets'][0]

    def create(self, vpc_resource, rt_resource):
        if self.sb_input.deploy:
            try:
                subnet = vpc_resource.create_subnet(
                    CidrBlock=self.sb_input.cidr,
                    AvailabilityZone=f"{REGION}{self.sb_input.zone}"
                )

                subnet.create_tags(
                    Tags=[{
                        "Key": "Name",
                        "Value": self.sb_input.name
                    }]
                )

                rt_resource.associate_with_subnet(SubnetId=subnet.id)
                logger.info(f"Subnet {self.sb_input.name} created successfully!")
                return self.validate()

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    logger.warning(f"Subnet {self.sb_input.name} already exist")

    def delete(self, sb_resource):
        """ Delete the subnets """
        sb_resource.delete()
        logger.info(f"Subnet {self.sb_input.name} deleted successfully")


def _validate_subnets(sb: SubnetManager):
    logger.debug("Validating Subnet...")
    response = sb.validate()

    if module.validate_resource('SubnetId', response):
        return

    module.save_state(response)


def _create_subnets(sb: SubnetManager):
    logger.debug("Creating Subnet...")
    state_container = module.get_state()
    # check if the state having the SubnetId key
    for vpc_entry in state_container.get('vpcs', []):
        index = module.extra_args['index']
        if vpc_entry.get('subnets', [])[index].get('SubnetId'):
            logger.info('Subnet is already present.')
            return

    vpc_id = module.get_resource_values(
        vpc_resource='subnets',
        resource_name=sb.sb_input.name,
        request='VpcId'
    )

    rt_id = module.get_resource_values(
        vpc_resource='subnets',
        resource_name=sb.sb_input.name,
        request='RouteTableId'
    )
    rt_resource = boto3.resource('ec2').RouteTable(rt_id)
    vpc_resource = boto3.resource('ec2').Vpc(vpc_id)

    response = sb.create(vpc_resource, rt_resource)
    if response:
        module.save_state(response)


def _delete_subnets(sb: SubnetManager):
    logger.debug("Deleting Subnet...")
    state_container = module.get_state()
    index = module.extra_args['index']
    for vpc_entry in state_container.get('vpcs', []):
        subnet = vpc_entry.get('subnets')[index]
        if subnet['name'] == sb.sb_input.name:
            if 'SubnetId' in subnet:
                sb_id = subnet['SubnetId']
                sb_resource = boto3.resource('ec2').Subnet(sb_id)
                sb.delete(sb_resource)
                module.update_state(data=sb.sb_input.model_dump())
            else:
                logger.warn("Subnet is Not Launched Yet...")


def run_module(action: str, data: dict, *args, **kwargs):
    inp = SubnetsInput(**data)
    sb = SubnetManager(inp)

    module.extra_args['index'] = kwargs['index']

    if action == 'validate':
        return _validate_subnets(sb)

    elif action == 'create':
        return _create_subnets(sb)

    elif action == 'delete':
        return _delete_subnets(sb)
