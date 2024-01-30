from devops.resources.vpc import Base, BaseAbstractmethod
from devops.models.vpc import ResourceCreationResponseModel, ResourceValidationResponseModel


class Subnet(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, subnet_cidr=None, region='ap-south-1', zone='a'):
        super().__init__(region=region)
        self.vpc_id = None
        self.sb_id = None
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.zone = zone
        self.subnet_cidr = subnet_cidr

    def validate(self):
        if self.vpc_id:
            response = self.client.describe_subnets(
                Filters=[
                    {
                        'Name': self.name,
                        'Values': [
                            self.vpc_id,
                        ],
                    },
                ],
            )
            return response

    def create(self, vpc_resource, rt_resouce):
        if not vpc_resource and not rt_resouce:
            return
        if self.state == 'available':
            subnet = vpc_resource.create_subnet(
                CidrBlock=self.subnet_cidr,
                AvailabilityZone=f"{self.region}{self.zone}"
            )

            self.sb_id = subnet.id
            subnet.create_tags(
                Tags=[{
                    "Key": "Name",
                    "Value": self.name
                }]
            )

            rt_resouce.associate_with_subnet(SubnetId=subnet.id)

            return ResourceCreationResponseModel(
                status=True,
                message="Subnet Created Successfully!",
                resource_id=self.sb_id
            ).model_dump()

    def delete(self):
        pass
