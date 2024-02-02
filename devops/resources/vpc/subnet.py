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

    def validate(self):
        message = ''
        _resources = []
        _ids = []
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
                _ids.append(sb_id)
                _resources.append(self.resource.Subnet(sb_id))
            available = True
            message = f"Subnet {self.name} is already exists"
        else:
            available = False
            message = f"Subnet {self.name} is not available"

        return ResourceValidationResponseModel(
            available=available,
            id=_ids,
            message=message,
            resource=_resources
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
                message = f"Subnet {self.name} created successfully!"
                _resource = self.resource.Subnet(subnet.id)

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    message = f"Subnet {self.name} already exist"
                    status = False

        return ResourceCreationResponseModel(
            status=status,
            message=message,
            resource_id=self.sb_id,
            resource=_resource
        ).model_dump()

    def delete(self):
        pass
