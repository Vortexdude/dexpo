from ..vpc import Base
from devops.models.config import ResponseModel


class Vpc(Base):

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
            print("VPC Available")

        else:
            print("VPC Not Available")

        return ResponseModel(available=self.vpc_available, id=self.vpc_id).model_dump()

    def create(self):
        pass

    def delete(self):
        pass











