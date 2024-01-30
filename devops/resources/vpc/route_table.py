from devops.models.vpc import ResourceValidationResponseModel
from devops.resources.vpc import Base


class RouteTable(Base):

    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1", destination_cidr_block=None):
        self.rt_available = False
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.id = ""

    def validate(self):
        try:

            response = self.client.describe_route_tables(Filters=[{
                "Name": "tag:Name",
                "Values": [self.name]
            }])
            if response['RouteTables']:
                self.rt_available = True
                print("RT Available")
            else:
                print("RT Not Available")

            return ResourceValidationResponseModel(available=self.rt_available, id=self.id).model_dump()

        except Exception as e:
            print(f"Something went wrong {e}")

    def create(self, vpc_resource, internet_gateway_id: str):
        if self.state == "present":
            if vpc_resource:
                routeTable = vpc_resource.create_route_table()
                if internet_gateway_id:
                    routeTable.create_route(
                        DestinationCidrBlock="0.0.0.0/0",
                        GatewayId=internet_gateway_id
                    )
                    routeTable.create_tags(Tags=[{
                        "Key": "Name",
                        "Value": self.name
                    }])
                    print("route table created successfully!")
                else:
                    print("Please provide the internet_gateway_id")
            else:
                print("Unknown vpc resource while Creating RouteTable")

    def delete(self):
        pass











