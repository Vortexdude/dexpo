from dexpo.src.resources.main import Base, BaseAbstractmethod


class RouteTable(Base, BaseAbstractmethod):
    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1", DestinationCidrBlock=None):
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

    def create(self, vpc_resource):
        if self.state == "present":
            routeTable = vpc_resource.create_route_table()
            routeTable.create_tags(Tags=[{
                "Key": "Name",
                "Value": self.name
            }])

            self.id = str(routeTable.id)
            if internet_gateway_id:
                routeTable.create_route(
                    DestinationCidrBlock="0.0.0.0/0",
                    GatewayId=internet_gateway_id
                )

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def route_table_validator(data: dict) -> dict:
    _rt_state = {}
    rt_obj = RouteTable(**data)
    rts = rt_obj.validate()
    if not rts:
        print("No Route Table found under the Name tag " + data['name'])
        #  Handle the exiting or skipping form here
    for rt in rts:
        _rt_state[data['name']] = rt

    return _rt_state


def create_route_table(data: dict):
    pass
