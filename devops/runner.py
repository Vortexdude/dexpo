from devops.utils import Utils
from devops.resources.vpc import Base
from devops.models.config import RootModel
from devops.models.vpc import ResourceValidationResponseModel

data = Utils.read_json('config.json')
config = RootModel(**data)


class VpcMaster:
    def __init__(self,
                 name: str = None,
                 state: str = False,
                 dry_run: bool = False,
                 region: str = None,
                 cidr_block: str = None,
                 route_table: dict = None,
                 internet_gateway: dict = None,
                 subnets: list[dict] = None,
                 *args, **kwargs
                 ):
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.region = region
        self.cidr_block = cidr_block
        self.route_table = route_table
        self.internet_gateway = internet_gateway
        self.subnets = subnets
        self._vpc_data = self.Vpc(self.name, self.state, self.dry_run, self.region, self.cidr_block).validate()

        print(self._vpc_data)

    class Vpc:
        def __init__(self, name, state, dry_run, region, cidr_block):
            self.vpc_available = False
            self.vpc_resource = None
            self.name = name
            self.state = state
            self.dry_run = dry_run
            self.region = region
            self.cidr_block = cidr_block
            self.filters = []
            self.vpc_id = None

        def validate(self):

            if self.cidr_block:
                self.filters.append({
                    'Name': 'cidr-block-association.cidr-block',
                    'Values': [self.cidr_block]
                })

            elif self.name:
                self.filters.append({
                    "Name": "tag:Name",
                    "Values": [self.name]

                })
            else:
                print("Something not parsed into the function")

            response = Base.client(self.region).describe_vpcs(Filters=self.filters)
            self.filters = []
            if response['Vpcs']:
                if not self.vpc_id:
                    self.vpc_id = response['Vpcs'][0]['VpcId']
                    self.vpc_resource = Base.resource(self.region).Vpc(self.vpc_id)
                self.vpc_available = True
                print("VPC Available")

            else:
                print("VPC Not Available")

            return ResourceValidationResponseModel(available=self.vpc_available, id=self.vpc_id).model_dump()


def runner(**kwargs):
    for vpc in kwargs['vpc']:
        VpcMaster(**vpc)


def run():
    runner(**config.model_dump())
