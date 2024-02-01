from devops.resources.vpc import Base, BaseAbstractmethod
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel


class InternetGateway(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=False, dry_run=False, region=None, *args, **kwargs):
        self.ig_resource = None
        self._id = ""
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.ig_name = name
        self.state = state
        self.dry_run = dry_run
        self.ig_available = False

    def validate(self):
        try:
            if self.state == "present":
                response = self.client.describe_internet_gateways(Filters=[{
                    "Name": "tag:Name",
                    "Values": [self.ig_name]
                }])

                if response['InternetGateways']:
                    self.ig_available = True
                    self._id = response['InternetGateways'][0]['InternetGatewayId']
                    self.ig_resource = self.resource.InternetGateway(self._id)
                    message = "Internet Gateway is Available"
                else:
                    message = "Internet Gateway is not Available"

                return ResourceValidationResponseModel(
                    available=self.ig_available,
                    id=self._id,
                    resource=self.ig_resource,
                    message=message

                ).model_dump()

        except Exception as e:
            print(f"Something went wrong {e}")

    def create(self, vpc_resource):
        response = self.client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.ig_name
                }]
            }]
        )
        if response['InternetGateway']:
            # print("Internet Gateway Created Successfully!")
            self._id = response['InternetGateway']['InternetGatewayId']
            self.ig_resource = self.resource.InternetGateway(self._id)
            if vpc_resource:
                vpc_resource.attach_internet_gateway(InternetGatewayId=self._id)
                # print(f"Internet gateway {self.ig_name} attached to VPC successfully!")

            else:
                print("Unknown VPC resource while launching the Internet gateway")
        else:
            print("There is an error while creating the InternetGateway")

        resource_status = True
        message = "Resource Launched successfully!"

        return ResourceCreationResponseModel(
            status=resource_status,
            message=message,
            resource_id=self._id,
            resource=self.ig_resource
        ).model_dump()

    def delete(self):
        pass











