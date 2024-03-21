from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, \
    DeleteResourceResponseModel
from devops.resources import Base, BaseAbstractmethod
from requests import get
import boto3.exceptions
from . import logger


class SecurityGroup(Base, BaseAbstractmethod):
    
    def __init__(self,
                 name: str = None,
                 state: str = False,
                 dry_run: bool = False,
                 description: str = "",
                 permissions: list = None):
        super().__init__(region='ap-south-1')
        self._resource = None
        self.id = ''
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.description = description
        self.permissions = permissions
        self.my_ip = get('https://api.ipify.org/').text
        self.sg_availability = False

    def validate(self):
        message = ''
        message = f'Security_Group {self.name} not exist'
        for ec2_security_group in self.client.describe_security_groups()['SecurityGroups']:
            if self.name == ec2_security_group['GroupName']:
                self.id = ec2_security_group['GroupId']
                self.sg_availability = True
                logger.info(f"Security Group {self.name} already exists")
                self._resource = self.resource.SecurityGroup(self.id)

    def to_dict(self, prop):
        return ResourceValidationResponseModel(
            type='sg',
            available=self.sg_availability,
            id=self.id,
            resource=self._resource,
            properties=prop
        ).model_dump()

    def create(self, vpc_id:str):
        message = ''
        secGroup = self.resource.create_security_group(
            GroupName=self.name,
            Description="%s" % self.description,
            VpcId=vpc_id,
            TagSpecifications=[{
                "ResourceType": 'security-group',
                "Tags": [{
                    "Key": "Name",
                    "Value": self.name
                }]
            }]
        )

        if secGroup.id:
            secGroup.authorize_ingress(
                IpPermissions=self.permissions
            )
            message = f'Security Group {self.name} Created Successfully!'
            logger.debug(f'Security Group {self.name} Created Successfully!')
            self.sg_availability = True
            self.id = secGroup.id
            self._resource = self.resource.SecurityGroup(self.id)
        else:
            message = f'Error while creating ingress rule in the security Group'
            logger.error(f'Error while creating ingress rule in the security Group')

        return ResourceCreationResponseModel(
            status=self.sg_availability,
            message=message,
            resource_id=self.id,
            resource=self._resource
        ).model_dump()


    def delete(self, sg_resource):
        """ Delete the Security Group """
        status = False
        message = ''
        if sg_resource:
            try:
                sg_resource.delete()
                status = True
                message = 'Security Group Deleted successfully'
                logger.warn(f'Security Group {self.name} Deleted successfully')
            except boto3.exceptions.Boto3Error as e:
                print(e)
        else:
            message = "Security Group doesnt exist"
            logger.error(f'Security Group {self.name} doesnt exist')

        return DeleteResourceResponseModel(
            status=status,
            message=message,
            resource='security_group'
        ).model_dump()
