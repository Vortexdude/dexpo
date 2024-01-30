from ..vpc import Base
from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel


class InternetGateway(Base):

    def __init__(self, name=None, state=False, dry_run=False, region=None, *args, **kwargs):
        self.ig_id = ""
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
                    self.ig_id = response['InternetGateways'][0]['InternetGatewayId']
                    print("IG Available")
                else:
                    print("IG Not Available")

                return ResourceValidationResponseModel(available=self.ig_available, id=self.ig_id).model_dump()

        except Exception as e:
            print(f"Something went wrong {e}")

    def create(self, vpc_id: str):
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
            print("Internet Gateway Created Successfully!")
            _ig = response['InternetGateway']['InternetGatewayId']
            self.ig_id = _ig
            if vpc_id:
                resource = self.resource.Vpc(vpc_id)
                resource.attach_internet_gateway(InternetGatewayId=self.ig_id)
                print(f"Internet gateway {self.ig_name} attached to VPC successfully!")

        else:
            print("There is an error")

        resource_status = True
        message = "Resource Launched successfully!"

        return ResourceCreationResponseModel(
            status=resource_status,
            message=message,
            resource_id=self.ig_id
        ).model_dump()

    def delete(self):
        pass











