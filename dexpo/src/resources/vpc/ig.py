from dexpo.src.resources.main import Base, BaseAbstractmethod


class InternetGateway(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1", *args, **kwargs):
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run

    def validate(self):
        response = self.client.describe_internet_gateways(Filters=[{
            "Name": "tag:Name",
            "Values": [self.name]
        }])

        return response['InternetGateways']

    def create(self):
        pass

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def internet_gateway_handler(data: dict):
    ig_state = {}
    ig_obj = InternetGateway(**data)
    igs = ig_obj.validate()
    if not igs:
        print("No Internet Gateway found under the Name tag " + data['name'])
    for ig in igs:
        ig_state[ig['InternetGatewayId']] = ig

    return ig_state
