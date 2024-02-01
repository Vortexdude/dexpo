from devops.resources.vpc import Base, BaseAbstractmethod
from devops.models.vpc import ResourceCreationResponseModel, ResourceValidationResponseModel
from devops.resources.vpc import ClientError

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

    def validate(self, vpc_id: str):
        available = False
        if vpc_id:
            response = self.client.describe_subnets(
                Filters=[
                    {
                        'Name': self.name,
                        'Values': [
                            vpc_id,
                        ],
                    },
                ],
            )

            if response:
                available = True
                print("Subnet Available")
            else:
                available = False
                print("Subnet Not Available")

        available = False
        print("Vpc not available so subnet is also not there")
        return ResourceValidationResponseModel(available=available, id="unknown").model_dump()

    def create(self, vpc_resource, rt_resouce):
        status = False
        message = ''

        if not vpc_resource and not rt_resouce:
            status = False
            message = 'Error with VPC resource or route table resource'

        if self.state == 'present':
            try:
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
                status = True
                message = "Subnet created successfully!"

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    message = 'Subnet already exist'
                    status = False

        return ResourceCreationResponseModel(
            status=status,
            message=message,
            resource_id=self.sb_id
        ).model_dump()

    def delete(self):
        pass
