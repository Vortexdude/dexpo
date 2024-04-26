from dexpo.src.resources.main import Base, BaseAbstractmethod
from dexpo.settings import logger


class VpcResource(Base, BaseAbstractmethod):

    def __init__(self, name=None, deploy=False, dry_run=False, CidrBlock=None, region='ap-south-1'):
        self.name = name
        self.deploy = deploy
        self.dry_run = dry_run
        self.CidrBlock = CidrBlock
        self.region = region
        self.filters = []
        self.vpc_resource = None
        super().__init__(region=region)

    def create(self) -> dict:
        """launch the vpc if the vpc not available"""

        if self.deploy:
            response = self.client.create_vpc(CidrBlock=self.CidrBlock)
            self.vpc_resource = self.resource.Vpc(response['Vpc']['VpcId'])
            self.vpc_resource.wait_until_available()
            self.vpc_resource.create_tags(
                Tags=[{
                    "Key": "Name",
                    "Value": self.name
                }]
            )  # adding name to the VPC

            logger.info(f"{self.name} VPC Created Successfully!")
            return response

    def validate(self) -> dict:
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""

        if self.CidrBlock:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.CidrBlock]
            })

        elif self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name]

            })
        else:
            logger.error("Something not parsed into the function")

        response = self.client.describe_vpcs(Filters=self.filters)
        if not response['Vpcs']:
            return {}

        return response['Vpcs'][0]

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass

    def xResource(self, id: str):
        return self.resource.Vpc(id)


def vpc_validator(data: dict, *args, **kwargs) -> dict:
    vpc_obj = VpcResource(**data)
    vpc = vpc_obj.validate()
    if not vpc:
        logger.info(f"No Vpc found under the name {data['name']} and CIDR block {data['CidrBlock']}")
        return {}
        #  Handle the exiting or skipping form here
    resource = vpc_obj.resource.Vpc(vpc['VpcId'])
    vpc.update({'resource': resource})
    return vpc


def create_vpc(data: dict, *args, **kwargs) -> tuple[dict, object]:
    vpc_obj = VpcResource(**data)
    response = vpc_obj.create()
    return response, vpc_obj.vpc_resource
