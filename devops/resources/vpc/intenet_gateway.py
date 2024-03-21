from devops.resources import Base, BaseAbstractmethod
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, DeleteResourceResponseModel
import boto3.exceptions
from . import logger


class InternetGateway(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, region=None, *args, **kwargs):
        self._resource = None
        self.id = ""
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.ig_available = False

    def validate(self):
        try:
            if self.state == "present":
                response = self.client.describe_internet_gateways(Filters=[{
                    "Name": "tag:Name",
                    "Values": [self.name]
                }])

                if response['InternetGateways']:
                    self.ig_available = True
                    self.id = response['InternetGateways'][0]['InternetGatewayId']
                    self._resource = self.resource.InternetGateway(self.id)
                    logger.info(f"Internet gateway {self.name} already exists")

        except Exception as e:
            print(f"Something went wrong {e}")
            logger.error(e)

    def to_dict(self, prop):
        return ResourceValidationResponseModel(
            type='ig',
            available=self.ig_available,
            id=self.id,
            resource=self._resource,
            properties=prop

        ).model_dump()


    def create(self, vpc_resource):
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
            # print("Internet Gateway Created Successfully!")
            self.id = response['InternetGateway']['InternetGatewayId']
            self._resource = self.resource.InternetGateway(self.id)
            if vpc_resource:
                vpc_resource.attach_internet_gateway(InternetGatewayId=self.id)
                # logger.debug(f"Internet gateway {self.name} attached to VPC successfully!")

            else:
                print("Unknown VPC resource while launching the Internet gateway")
                logger.error("Unknown VPC resource while launching the Internet gateway")
        else:
            print("There is an error while creating the InternetGateway")

        resource_status = True
        message = f"Internet Gateway {self.name} Created Successfully!"
        logger.debug(f"Internet Gateway {self.name} Created Successfully!")

        return ResourceCreationResponseModel(
            status=resource_status,
            message=message,
            resource_id=self.id,
            resource=self._resource
        ).model_dump()

    def delete(self, vpc_resource, vpc_id: str):
        """ Detach and delete the internet-gateway """
        message = ''
        status = False
        if vpc_resource and vpc_id:
            internet_gateways = vpc_resource.internet_gateways.all()
            if internet_gateways:
                for internet_gateway in internet_gateways:
                    try:
                        print("Detaching and Removing igw-id: ", internet_gateway.id)
                        internet_gateway.detach_from_vpc(
                            VpcId=vpc_id
                        )
                        internet_gateway.delete(
                            # DryRun=True
                        )
                        message = "Internet Gateway Deleted Successfully"
                        logger.warn("Internet Gateway Deleted Successfully")
                        status = True
                    except boto3.exceptions.Boto3Error as e:
                        print(e)
        else:
            message = 'Internet gateway doesnt exist'

        return DeleteResourceResponseModel(
            status=status,
            message=message,
            resource='internet_gateway'
        ).model_dump()
