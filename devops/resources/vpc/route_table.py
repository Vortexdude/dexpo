from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, \
    DeleteResourceResponseModel
from devops.resources.vpc import Base
import boto3.exceptions

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
                message = f"Route Table {self.name} is already exists"
            else:
                message = f"Route Table {self.name} is not available"

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

                    message = f"route table {self.name} created successfully!"
                    status = True
                    self.rt_resource = self.resource.RouteTable(self.rt_id)
                else:
                    message = "Invalid internet_gateway_id. rt-63"
                    status = False
            else:
                print("Invalid vpc_resource. rt-66")

            return ResourceCreationResponseModel(
                status=status,
                message=message,
                resource_id=self.rt_id,
                resource=self.rt_resource
            ).model_dump()

    def delete(self, rt_resource):
        status = False
        message = ''
        if rt_resource:
            try:
                rt_resource.delete()
                status = True
                message = 'Route Table deleted successfully'
            except boto3.exceptions.Boto3Error as e:
                print(e)
        else:
            status = False
            message = 'Route Table doesnt exist'

        return DeleteResourceResponseModel(
            status=status,
            message=message,
            resource='route_table'
        ).model_dump()
