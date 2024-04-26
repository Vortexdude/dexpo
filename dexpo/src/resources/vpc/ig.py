"""
Create an Internet Gateway and attach it to a specified VPC.

Parameters:
    self.name (str): The ID of the VPC to which the Internet Gateway will be attached.
    self.deploy (bool):
    self.dry_run (bool):
    vpc_resource (object):
Returns:
    dict: A dictionary containing information about the created Internet Gateway.

Raises:
    botocore.exceptions.ClientError: If the Internet Gateway creation fails.

Example:
    >>> from path import create_internet_gateway
    >>> ig_id, ig_resource = create_internet_gateway(data, vpc_resource)
"""


from dexpo.src.resources.main import Base, BaseAbstractmethod
from dexpo.settings import logger


class InternetGateway(Base, BaseAbstractmethod):

    def __init__(self, name=None, deploy=None, dry_run=False, region="ap-south-1", *args, **kwargs):
        super().__init__(region=region)
        self.name = name
        self.deploy = deploy
        self.dry_run = dry_run

    def validate(self) -> dict:
        response = self.client.describe_internet_gateways(Filters=[{
            "Name": "tag:Name",
            "Values": [self.name]
        }])
        if not response['InternetGateways']:
            return {}

        return response['InternetGateways'][0]

    def create(self, vpc_resource) -> dict:
        response = self.client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.name
                }]
            }]
        )

        if response['InternetGateway']:
            logger.info(f"Internet Gateway {self.name} Created Successfully!")
            ig_id = response['InternetGateway']['InternetGatewayId']
            if vpc_resource:
                vpc_resource.attach_internet_gateway(InternetGatewayId=ig_id)
                logger.info(f"Internet Gateway {self.name} attached to vpc {ig_id} Successfully!")

                return response

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def internet_gateway_validator(data: dict) -> dict:
    ig_obj = InternetGateway(**data)
    ig = ig_obj.validate()
    if not ig:
        logger.info("No Internet Gateway found under the Name tag " + data['name'])
        return {}

    resource = ig_obj.resource.InternetGateway(ig['InternetGatewayId'])
    ig.update({'resource': resource})
    return ig


def create_internet_gateway(data: dict, vpc_resource) -> tuple[dict, object]:
    ig_obj = InternetGateway(**data)
    response = ig_obj.create(vpc_resource)
    return response, ig_obj.resource.InternetGateway(response['InternetGateway']['InternetGatewayId'])
