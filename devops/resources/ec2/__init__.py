from settings import logger
from devops.resources import Base, BaseAbstractmethod
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel


class Ec2(Base, BaseAbstractmethod):
    def __init__(self, name, state, instance_type, ami, key_file, subnet, vpc, region, security_groups, dry_run=False):
        super().__init__(region)
        self.name = name
        self.state = state,
        self.instance_type = instance_type
        self.ami = ami
        self.key_file = key_file
        self.subnet = subnet,
        self.security_groups = security_groups
        self.vpc = vpc
        self.available = False
        self.instance_id = ''

    def validate(self, vpc_resource=None):
        # inst_names = [tag['Value'] for i in vpc.instances.all() for tag in i.tags if tag['Key'] == 'Name']

        if not vpc_resource:
            # self._resource = self.resource.Vpc('vpc-08a62c4b70250463b')
            vpc_rs = self.resource.Vpc('vpc-08a62c4b70250463b')
            for instance in vpc_rs.instances.all():
                print(instance)
                for tag in instance.tags:
                    if tag['Key'] == 'Name':
                        if tag['Value'] == self.name:
                            self.available = True
                            self.instance_id = instance.instance_id
                            self._resource = instance
                            print(self.instance_id)
                            if instance.state['Name'] != 'running':
                                logger.warn("Instance is not in running state")

        else:
            logger.error("Vpc Resource does not exist")

    def to_dict(self, prop: dict):
        return ResourceValidationResponseModel(
            available=self.available,
            id=self.instance_id,
            resource=self._resource,
            properties=prop,
            type='ec2'
        ).model_dump()

    def create(self, subnet_id: str, security_group_ids: list):
        resource_status = False
        if subnet_id and security_group_ids:
            ec2Instances = self.resource.create_instances(
                ImageId=self.ami,
                InstanceType=self.instance_type,
                MaxCount=1,
                MinCount=1,
                NetworkInterfaces=[{
                    'SubnetId': subnet_id, 'DeviceIndex': 0,
                    'AssociatePublicIpAddress': True, 'Groups': security_group_ids
                }],
                KeyName=self.key_file
            )
            instance = ec2Instances[0]
            instance.create_tags(
                Tags=[{"Key": "Name", "Value": self.name}]
            )
            instance.wait_until_running()
            resource_status = True
            self.instance_id = instance.id
            logger.warning('Connect Ec2 instance with the following SSH command once initializing process gets completed.')
            logger.warning(f'ssh -i {self.key_file}.pem ubuntu@{instance.public_ip_address}')
            return ResourceCreationResponseModel(
                status=resource_status,
                message="",
                resource_id=self.instance_id,
                resource=instance
            ).model_dump()

        else:
            logger.error("Subnet or security_group id is missing")

    def delete(self):
        pass
