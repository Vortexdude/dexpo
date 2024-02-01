from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel
from devops.resources.vpc import Base


class RouteTable(Base):

    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1", destination_cidr_block=None):
        self.rt_resource = None
        self.rt_available = False
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.rt_id = ""

    def validate(self):
        try:

            response = self.client.describe_route_tables(Filters=[{
                "Name": "tag:Name",
                "Values": [self.name]
            }])
            if response['RouteTables']:
                self.rt_available = True
                self.rt_id = response['RouteTables'][0]['RouteTableId']
                self.rt_resource = self.resource.RouteTable(self.rt_id)
                message = "Route Table is available"
            else:
                message = "Route Table is not available"

            return ResourceValidationResponseModel(
                available=self.rt_available,
                id=self.rt_id,
                resource=self.rt_resource,
                message=message
            ).model_dump()

        except Exception as e:
            print(f"Something went wrong {e}")

    def create(self, vpc_resource, internet_gateway_id: str):
        message = ""
        status = False
        if self.state == "present":
            if vpc_resource:
                routeTable = vpc_resource.create_route_table()
                self.rt_id = str(routeTable.id)
                if internet_gateway_id:
                    routeTable.create_route(
                        DestinationCidrBlock="0.0.0.0/0",
                        GatewayId=internet_gateway_id
                    )
                    routeTable.create_tags(Tags=[{
                        "Key": "Name",
                        "Value": self.name
                    }])

                    message = "route table created successfully!"
                    status = True
                    self.rt_resource = self.resource.RouteTable(self.rt_id)
                else:
                    message = "Please provide the internet_gateway_id"
                    status = False
            else:
                print("Unknown vpc resource while Creating RouteTable")

            return ResourceCreationResponseModel(
                status=status,
                message=message,
                resource_id=self.rt_id,
                resource=self.rt_resource
            ).model_dump()

    def delete(self):
        pass











