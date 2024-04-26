from dexpo.src.resources.main import Base, BaseAbstractmethod
from botocore.exceptions import ClientError
from dexpo.settings import logger


class Subnet(Base, BaseAbstractmethod):

    def __init__(self, name=None, deploy=None, dry_run=False, cidr=None, route_table=None, region='ap-south-1',
                 zone='a'):
        super().__init__(region=region)
        self.route_table = route_table
        self.name = name
        self.deploy = deploy
        self.dry_run = dry_run
        self.zone = zone
        self.cidr = cidr

    def validate(self) -> dict:
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
        if not response['Subnets']:
            logger.info("No subnets found in the cloud")
            return {}

        return response['Subnets'][0]

    def create(self, vpc_resource, rt_resource):
        if self.deploy:
            try:
                subnet = vpc_resource.create_subnet(
                    CidrBlock=self.cidr,
                    AvailabilityZone=f"{self.region}{self.zone}"
                )

                subnet.create_tags(
                    Tags=[{
                        "Key": "Name",
                        "Value": self.name
                    }]
                )

                rt_resource.associate_with_subnet(SubnetId=subnet.id)
                logger.info(f"Subnet {self.name} created successfully!")
                return subnet.id

            except ClientError as e:
                if e.response['Error']['Code'] == 'InvalidSubnet.Conflict':
                    logger.warning(f"Subnet {self.name} already exist")

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def sb_validator(data: dict, *args, **kwargs) -> dict:
    sb_obj = Subnet(**data)
    subnet = sb_obj.validate()
    if not subnet:
        logger.info("No Subnets found under the name tag " + data['name'])
        return {}

    resource = sb_obj.resource.Subnet(subnet['SubnetId'])
    subnet.update({'resource': resource})
    return subnet


def create_subnet(data: dict, vpc_resource, rt_resource, *args, **kwargs) -> tuple:
    sb_object = Subnet(**data)
    sb_id = sb_object.create(vpc_resource, rt_resource)
    return sb_id, sb_object.resource.Subnet(sb_id)
