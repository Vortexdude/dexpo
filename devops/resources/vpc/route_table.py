from devops.models.config import ResponseModel
from devops.resources.vpc import Base


class RouteTable(Base):

    def __init__(self, name=None, state=None, dry_run=False, region="ap-south-1"):
        self.rt_available = False
        region = region if region else "ap-south-1"
        super().__init__(region=region)
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.id = ""

    def validate(self):
        if self.name:
            response = self.client.describe_route_tables(Filters=[{
                "Name": "tag:Name",
                "Values": [self.name]
            }])
            if response['RouteTables']:
                self.rt_available = True
                print("RT Available")
            else:
                print("RT Not Available")

        return ResponseModel(available=self.rt_available, id=self.id).model_dump()

    def create(self):
        pass

    def delete(self):
        pass











