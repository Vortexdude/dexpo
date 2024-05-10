"""These are docstrings basically a documentation of the module"""

import boto3
from typing import List
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
    def __init__(self, sg_input: SecurityGroupInput):
        self.sg_input = sg_input
        self.ec2_client = boto3.client("ec2")
        self.ec2_resource = boto3.resource('ec2')

    def validate(self) -> dict:
        sg_groups = []
        for ec2_security_group in self.ec2_client.describe_security_groups()['SecurityGroups']:
            if self.sg_input.name == ec2_security_group['GroupName']:
                sg_groups.append(ec2_security_group)
        if not sg_groups:
            return {}
        else:
            return sg_groups[0]

    def create(self, vpc_id):
        secGroup = self.ec2_resource.create_security_group(
            GroupName=self.sg_input.name,
            Description="%s" % self.sg_input.description,
            VpcId=vpc_id,
            TagSpecifications=[{
                "ResourceType": 'security-group',
                "Tags": [{
                    "Key": "Name",
                    "Value": self.sg_input.name
                }]
            }]
        )

        if secGroup.id:
            secGroup.authorize_ingress(
                IpPermissions=self.sg_input.model_dump()['permissions']
            )
            logger.info(f'Security Group {self.sg_input.name} Created Successfully!')
        else:
            logger.error('Error while creating ingress rule in the security Group')

        return self.validate()

    def delete(self, sg_resource):
        sg_resource.delete()
        logger.info(f"Security Group {self.sg_input.name} Deleted Successfully.")


def _validate_security_group(sg: SecurityGroupManager):
    logger.debug("Validating Security Groups...")
    response = sg.validate()
    if module.validate_resource('GroupId', response):
        return

    module.save_state(response)


def _create_security_group(sg: SecurityGroupManager):
    logger.debug("Creating Security Groups...")
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        index = module.extra_args['index']
        if vpc_entry.get('security_groups', [])[index].get('GroupId'):
            logger.info('Security Group is already present.')
            return

    vpc_id = module.get_resource_values(
        vpc_resource='security_groups',
        resource_name=sg.sg_input.name,
        request='VpcId'
    )
    response = sg.create(vpc_id)
    if response:
        module.save_state(response)


def _delete_security_group(sg: SecurityGroupManager):
    logger.debug("Deleting Security Groups...")
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        index = int(module.extra_args['index'])
        security_group = vpc_entry.get('security_groups')[index]
        if security_group.get('name') == sg.sg_input.name:
            if 'GroupId' in security_group:
                sg_id = security_group['GroupId']
                sg_resource = boto3.resource('ec2').SecurityGroup(sg_id)
                sg.delete(sg_resource)
                module.update_state(data=sg.sg_input.model_dump())
            else:
                logger.warn("securityGroup is Not Launched Yet...")


def run_module(action: str, data: dict, *args, **kwargs):
    inp = SecurityGroupInput(**data)
    sg = SecurityGroupManager(inp)
    if 'index' in kwargs:
        module.extra_args['index'] = kwargs['index']

    if action == 'validate':
        return _validate_security_group(sg)

    elif action == 'create':
        return _create_security_group(sg)

    elif action == 'delete':
        return _delete_security_group(sg)
