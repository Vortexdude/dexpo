from devops.resources import Base, BaseAbstractmethod
from devops.models.vpc import ResourceCreationResponseModel, ResourceValidationResponseModel, \
    DeleteResourceResponseModel
from devops.resources import ClientError
import boto3.exceptions


class Subnet(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, cidr=None, region='ap-south-1', zone='a'):
        super().__init__(region=region)
        self._resource = None
        self.vpc_id = None
        self.id = None
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.zone = zone
        self.cidr = cidr
        self.availability = False
    def validate(self):
        message = ''
        available = False
        response = self.client.describe_subnets(
            Filters=[
                {
                    'Name': "tag:Name",
                    'Values': [
                        self.name,
                    ],
                },
            ],
        )

        if response['Subnets']:
            for subnet in response['Subnets']:
                sb_id = subnet['SubnetId']
                self.id = sb_id
                self._resource = self.resource.Subnet(self.id)
            available = True
            message = f"Subnet {self.name} is already exists"
        else:
            available = False
            message = f"Subnet {self.name} is not available"

        return ResourceValidationResponseModel(
            available=available,
            id=self.id,
            message=message,
            resource=self._resource
        ).model_dump()

    def to_dict(self, prop):
        return ResourceValidationResponseModel(
            available=self.availability,
            id=self.id,
            resource=self._resource,
            properties=prop
        ).model_dump()

    def create(self, vpc_resource, rt_resouce):
        _resource = None
        status = False
        message = ''

        if not vpc_resource and not rt_resouce:
            status = False
            message = 'Error with VPC resource or route table resource'

        if self.state == 'present':
            try:
                subnet = vpc_resource.create_subnet(
                    CidrBlock=self.cidr,
                    AvailabilityZone=f"{self.region}{self.zone}"
                )

                self.id = subnet.id
                subnet.create_tags(
                    Tags=[{
                        "Key": "Name",
                        "Value": self.name
                    }]
                )

                rt_resouce.associate_with_subnet(SubnetId=subnet.id)
                status = True
                message = f"Subnet {self.name} created successfully!"
                _resource = self.resource.Subnet(subnet.id)

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    message = f"Subnet {self.name} already exist"
                    status = False

        return ResourceCreationResponseModel(
            status=status,
            message=message,
            resource_id=self.id,
            resource=_resource
        ).model_dump()

    def delete(self, sb_resource):
        """ Delete the subnets """
        status = False
        message = ''
        if sb_resource:
            try:
                if sb_resource:
                    print(f"Removing sub-id with....")
                    sb_resource.delete()
                    status = True
                    message = 'Subnet deleted successfully'
            except boto3.exceptions.Boto3Error as e:
                print(e)
        else:
            message = 'Subnet doesnt exist'

        return DeleteResourceResponseModel(
            status=status,
            message=message,
            resource='security_group'
        ).model_dump()
