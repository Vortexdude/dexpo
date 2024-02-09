from devops.resources import Base, BaseAbstractmethod
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, \
    DeleteResourceResponseModel
import boto3.exceptions

"""
The response* model used to send the data as per the required flied
so add the necessary filed in the response model to kep the work efficient
try to check the model if needed and also add the validation method and message

"""


class Vpc(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=False, dry_run=False, vpc_id='', cidr_block=None, region=None, *args, **kwargs):
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.id = vpc_id
        self.cidr_block = cidr_block
        self.dry_run = dry_run
        self.filters = []
        self.vpc_available = False

    def validate(self):
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""

        if self.id:
            self.filters.append({
                "Name": "vpc-id",
                "Values": [self.id]
            })

        elif self.cidr_block:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.cidr_block]
            })

        elif self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name]

            })
        else:
            print("Something not parsed into the function")

        response = self.client.describe_vpcs(Filters=self.filters)
        self.filters = []
        if response['Vpcs']:
            if not self.id:
                self.id = response['Vpcs'][0]['VpcId']
                self.vpc_resource = self.resource.Vpc(self.id)
            self.vpc_available = True

    def to_dict(self, prop):
        return ResourceValidationResponseModel(
            available=self.vpc_available,
            id=self.id,
            resource=self.vpc_resource,
            properties=prop
        ).model_dump()

    def create(self):
        """launch the vpc if the vpc not available"""
        resource_status = False
        message = ""
        try:
            if self.state == "present":
                response = self.client.create_vpc(CidrBlock=self.cidr_block)
                self.id = response['Vpc']['VpcId']
                self.vpc_resource = self.resource.Vpc(self.id)
                self._wait_until_available(self.resource.Vpc(self.id), "VPC")
                print(f"VPC {self.name} Attaching name to the VPC")
                self._add_tags(self.name)  # adding name to the VPC
                resource_status = True
                message = f"Vpc {self.name} Created Successfully!"

        except Exception as e:
            print(f"There are some error in launching the vpc {e}")

        return ResourceCreationResponseModel(
            status=resource_status,
            message=message,
            resource_id=self.id,
            resource=self.vpc_resource
        ).model_dump()

    def _add_tags(self, vpc_name: str):
        self.vpc_resource.create_tags(
            Tags=[{
                "Key": "Name",
                "Value": vpc_name
            }]
        )

    def _wait_until_available(self, resource, resource_name):
        """Wait until the resource is available."""

        resource.wait_until_available()
        print(f"{resource_name} {self.name} is available.")

    def delete(self):
        """ Delete the VPC """
        status = False
        message = ""
        if self.vpc_resource:
            try:
                self.vpc_resource.delete()
                status = True
                message = "Vpc Deleted successfully"
            except boto3.exceptions.Boto3Error as e:
                print(e)
        else:
            status = False
            message = "Vpc Doesnt Exist"

        return DeleteResourceResponseModel(
            status=status,
            message=message,
            resource='vpc'
        ).model_dump()
