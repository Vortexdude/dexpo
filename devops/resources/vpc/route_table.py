from devops.models.vpc import ResourceValidationResponseModel, ResourceCreationResponseModel, \
    DeleteResourceResponseModel
from devops.resources import Base, BaseAbstractmethod
import boto3.exceptions


class RouteTable(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1", DestinationCidrBlock=None):
        self._resource = None
        self.rt_available = False
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.id = ""
        self.DestinationCidrBlock = DestinationCidrBlock

    def validate(self):
        try:

            response = self.client.describe_route_tables(Filters=[{
                "Name": "tag:Name",
                "Values": [self.name]
            }])
            if response['RouteTables']:
                self.rt_available = True
                self.id = response['RouteTables'][0]['RouteTableId']
                self._resource = self.resource.RouteTable(self.id)

        except Exception as e:
            print(f"Something went wrong {e}")

    def to_dict(self, prop):
        return ResourceValidationResponseModel(
            available=self.rt_available,
            id=self.id,
            resource=self._resource,
            properties=prop
        ).model_dump()

    def create(self, vpc_resource, internet_gateway_id: str):
        message = ""
        status = False
        if self.state == "present":
            if vpc_resource:
                routeTable = vpc_resource.create_route_table()
                self.id = str(routeTable.id)
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
                    self._resource = self.resource.RouteTable(self.id)
                else:
                    message = "Invalid internet_gateway_id. rt-63"
                    status = False
            else:
                print("Invalid vpc_resource. rt-66")

            return ResourceCreationResponseModel(
                status=status,
                message=message,
                resource_id=self.id,
                resource=self._resource
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
