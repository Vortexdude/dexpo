"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from pydantic import BaseModel
from typing import Optional

extra_args = dict(
    resource_type='dict',
)


class Ec2Input(BaseModel):
    name: str
    deploy: bool
    instance_type: str
    ami: str
    key_file: str
    region: str
    subnet: str
    vpc: str
    security_groups: Optional[list] = None


module = DexpoModule(
    base_arg=Ec2Input,
    extra_args=extra_args,
    module_type='ec2'
)
logger = module.logger


class Ec2Manager:
    """Class for managing EC2 instances."""
    SERVICE = 'ec2'

    def __init__(self, ec2_input: Ec2Input):
        """Initialize EC2 manager."""
        self.ec2_input = ec2_input
        self.ec2_client = boto3.client(self.SERVICE, region_name=self.ec2_input.region)
        self.ec2_resource = boto3.resource(self.SERVICE, region_name=self.ec2_input.region)

    def create(self, subnet_id, security_group_ids: list):
        """Create EC2 instance."""
        if not subnet_id and not security_group_ids:
            logger.error("Subnet or security_group id is missing")
            return False

        ec2Instances = self.ec2_resource.create_instances(
            ImageId=self.ec2_input.ami,
            InstanceType=self.ec2_input.instance_type,
            MaxCount=1,
            MinCount=1,
            NetworkInterfaces=[{
                'SubnetId': subnet_id, 'DeviceIndex': 0,
                'AssociatePublicIpAddress': True, 'Groups': security_group_ids
            }],
            KeyName=self.ec2_input.key_file
        )
        instance = ec2Instances[0]
        instance.create_tags(
            Tags=[{"Key": "Name", "Value": self.ec2_input.name}]
        )
        instance.wait_until_running()
        logger.info('Connect Ec2 instance with the following SSH command once initializing process gets '
                    'completed.')
        logger.info(f'ssh -i {self.ec2_input.key_file}.pem ubuntu@{instance.public_ip_address}')
        logger.info(f"{instance.instance_id}")
        return instance.instance_id

    def _validate_wrapper(self, vpc_id=None, instance_id=None):
        """Wrapper for validating EC2 instance."""
        instance_ids = []
        filters = [{'Name': 'tag:Name', 'Values': [self.ec2_input.name]}]
        if vpc_id:
            filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
        if instance_id:
            instance_ids.append(instance_id)

        response = self.ec2_client.describe_instances(Filters=filters, InstanceIds=instance_ids)

        # Extract instance details from the response
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)

    def validate(self, vpc_id=None, instance_id=None):
        """Validate EC2 instance."""
        instance_ids = []
        filters = [{'Name': 'tag:Name', 'Values': [self.ec2_input.name]}]
        if vpc_id:
            filters.append({'Name': 'vpc-id', 'Values': [vpc_id]})
        if instance_id:
            instance_ids.append(instance_id)

        response = self.ec2_client.describe_instances(Filters=filters, InstanceIds=instance_ids)

        # Extract instance details from the response
        instances = []
        for reservation in response['Reservations']:
            for instance in reservation['Instances']:
                instances.append(instance)
        if not instances:
            return {}
        from itertools import islice
        data = list(islice(instances[0].items(), 5))
        return data

    def delete(self, instance_id):
        """ Delete the VPC """
        if not instance_id:
            return

        self.ec2_client.terminate_instances(
            InstanceIds=[
                instance_id
            ],
            DryRun=False
        )
        ec2_resource = self.ec2_resource.Instance(instance_id)
        ec2_resource.wait_until_terminated(
            Filters=[
                {
                    'Name': 'instance-id',
                    'Values': [
                        instance_id,
                    ]
                },
            ],
        )
        return True


def _validate_ec2(ec2: Ec2Manager) -> None:
    logger.debug("Validating ec2........")
    vpc_id = module.get_resource_values('vpc', 'ec2', 'VpcId')
    if not vpc_id:
        logger.info("First launch VPC first")
        return

    response = ec2.validate(vpc_id)
    _current_state = module.get_state()
    for _ec2 in _current_state.get('ec2', []):
        if _ec2['name'] == ec2.ec2_input.name:
            instance_id = next((i[1] for i in response if i[0] == 'InstanceId'), None)
            if instance_id == _ec2.get('InstanceId', ''):
                return
            if not instance_id and _ec2.get('InstanceId', ''):
                logger.warn("someone deleted the resource from the cloud.")
                logger.info("Fixing . . . .")
                module.update_state(ec2.ec2_input.model_dump())
                return
            if instance_id and not _ec2.get('InstanceId', ''):
                module.update_state(response)


def _create_ec2(ec2: Ec2Manager) -> None:
    logger.debug("Creating ec2........")
    state_container: dict = module.get_state()
    # check if the state having the InstanceId key
    for ec2_state in state_container.get('ec2', []):
        if ec2_state.get('InstanceId', ''):
            logger.info('Ec2 already exist')
            return

    subnet_id = module.get_resource_values('vpc', 'ec2', 'SubnetId')
    sg_ids = module.get_resource_values('vpc', 'ec2', 'SecurityGroupId')
    instance_id = ec2.create(subnet_id, sg_ids)
    if instance_id:
        response = ec2.validate(instance_id=instance_id)
        module.save_state(response)


def _delete_ec2(ec2: Ec2Manager) -> None:
    logger.debug("Deleting ec2...")
    state_container = module.get_state()
    for _ec2 in state_container.get('ec2', []):
        instance_id = _ec2.get('InstanceId', '')
        if not instance_id:
            logger.warn("Ec2 instance is Not Launched Yet...")
            return
        ec2.delete(instance_id)
        module.update_state(ec2.ec2_input.model_dump())


def run_module(action: str, data: dict):
    inp = Ec2Input(**data)
    vpc = Ec2Manager(inp)
    module.base_args = vpc.ec2_input
    module.extra_args['action'] = action
    if action == 'validate':
        return _validate_ec2(vpc)

    elif action == 'create':
        return _create_ec2(vpc)

    elif action == 'delete':
        return _delete_ec2(vpc)
