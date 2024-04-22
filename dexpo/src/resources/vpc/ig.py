from dexpo.src.resources.main import Base, BaseAbstractmethod


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
            print(f"Internet Gateway {self.name} Created Successfully!")
            ig_id = response['InternetGateway']['InternetGatewayId']
            if vpc_resource:
                vpc_resource.attach_internet_gateway(InternetGatewayId=ig_id)
                print(f"Internet Gateway {self.name} attached to vpc {ig_id} Successfully!")

                return ig_id

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def internet_gateway_validator(data: dict) -> dict:
    ig_obj = InternetGateway(**data)
    ig = ig_obj.validate()
    if not ig:
        print("No Internet Gateway found under the Name tag " + data['name'])
        return {}

    resource = ig_obj.resource.InternetGateway(ig['InternetGatewayId'])
    ig.update({'resource': resource})
    return ig


def create_internet_gateway(data: dict, vpc_resource) -> tuple:
    ig_obj = InternetGateway(**data)
    id = ig_obj.create(vpc_resource)
    return id, ig_obj.resource.InternetGateway(id)
