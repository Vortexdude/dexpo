from ..vpc import Base, BaseAbstractmethod
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, \
    DeleteResourceResponseModel
import boto3.exceptions

"""
The response* model used to send the data as per the required flied
so add the necessary filed in the response model to kep the work efficient
try to check the model if needed and also add the validation method and message

"""


class Vpc(Base, BaseAbstractmethod):

    def __init__(self, vpc_name=None, state=False, dry_run=False, vpc_id='', vpc_cidr=None, region=None, *args, **kwargs):
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.vpc_name = vpc_name
        self.state = state
        self.vpc_id = vpc_id
        self.vpc_cidr = vpc_cidr
        self.dry_run = dry_run
        self.filters = []
        self.vpc_available = False

    def validate(self):
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""

        if self.vpc_id:
            self.filters.append({
                "Name": "vpc-id",
                "Values": [self.vpc_id]
            })

        elif self.vpc_cidr:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.vpc_cidr]
            })

        elif self.vpc_name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.vpc_name]

            })
        else:
            print("Something not parsed into the function")

        response = self.client.describe_vpcs(Filters=self.filters)
        self.filters = []
        if response['Vpcs']:
            if not self.vpc_id:
                self.vpc_id = response['Vpcs'][0]['VpcId']
                self.vpc_resource = self.resource.Vpc(self.vpc_id)
            self.vpc_available = True
            message = f"Vpc {self.vpc_name} is already exists"

        else:
            message = f"Vpc {self.vpc_name} is not available"

        return ResourceValidationResponseModel(
            available=self.vpc_available,
            id=self.vpc_id,
            resource=self.vpc_resource,
            message=message
        ).model_dump()

    def create(self):
        """launch the vpc if the vpc not available"""
        resource_status = False
        message = ""
        try:
            if self.state == "present":
                response = self.client.create_vpc(CidrBlock=self.vpc_cidr)
                self.vpc_id = response['Vpc']['VpcId']
                self.vpc_resource = self.resource.Vpc(self.vpc_id)
                self._wait_until_available(self.resource.Vpc(self.vpc_id), "VPC")
                print(f"VPC {self.vpc_name} Attaching name to the VPC")
                self._add_tags(self.vpc_name)  # adding name to the VPC
                resource_status = True
                message = f"Vpc {self.vpc_name} Created Successfully!"

        except Exception as e:
            print(f"There are some error in launching the vpc {e}")

        return ResourceCreationResponseModel(
            status=resource_status,
            message=message,
            resource_id=self.vpc_id,
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
        print(f"{resource_name} {self.vpc_name} is available.")

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











