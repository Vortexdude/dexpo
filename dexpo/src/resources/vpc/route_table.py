from dexpo.src.resources.main import Base, BaseAbstractmethod
from dexpo.settings import logger


class RouteTable(Base, BaseAbstractmethod):
    def __init__(self, name=None, deploy=None, dry_run=False, region="ap-south-1", DestinationCidrBlock=None):
        self.id = ''
        self.name = name
        self.deploy = deploy
        self.dry_run = dry_run
        self.DestinationCidrBlock = DestinationCidrBlock
        self.region = region
        super().__init__(region=region)

    def validate(self) -> dict:
        response = self.client.describe_route_tables(Filters=[{
            "Name": "tag:Name",
            "Values": [self.name]
        }])
        if not response['RouteTables']:
            return {}
        else:
            return response['RouteTables'][0]

    def create(self, vpc_resource, ig_id: str):
        if self.deploy:
            routeTable = vpc_resource.create_route_table()
            routeTable.create_tags(Tags=[{
                "Key": "Name",
                "Value": self.name
            }])
            self.id = str(routeTable.id)
            if ig_id:
                routeTable.create_route(
                    DestinationCidrBlock="0.0.0.0/0",
                    GatewayId=ig_id
                )

                logger.info(f"Route Table {self.name} Created Successfully!")
            return self.id

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def route_table_validator(data: dict) -> dict:
    rt_obj = RouteTable(**data)
    rt = rt_obj.validate()
    if not rt:
        logger.info("No Route Table found under the Name tag " + data['name'])
        #  Handle the exiting or skipping form here
        return {}

    resource = rt_obj.resource.RouteTable(rt['RouteTableId'])
    rt.update({'resource': resource})
    return rt


def create_route_table(data: dict, vpc_resource, ig_id) -> tuple:
    rt_obj = RouteTable(**data)
    rt_id = rt_obj.create(vpc_resource, ig_id)
    return rt_id, rt_obj.resource.RouteTable(rt_id)
