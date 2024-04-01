from dexpo.src.resources.main import Base, BaseAbstractmethod


class RouteTable(Base, BaseAbstractmethod):
    def __init__(self,  name=None, state=None, dry_run=False, region="ap-south-1", DestinationCidrBlock=None):
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.DestinationCidrBlock = DestinationCidrBlock
        self.region = region
        super().__init__(region=region)

    def validate(self):
        response = self.client.describe_route_tables(Filters=[{
            "Name": "tag:Name",
            "Values": [self.name]
        }])
        return response['RouteTables']


    def create(self):
        pass

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass
