import boto3
from devops.models.config import RootModel
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.utils import Utils

# convert the json into dictionary
_json = Utils.read_json('config.json')

# pass the data into the Model fto get the accurate data
config = RootModel(**_json)


class BaseVpcInit:
    def __init__(self):
        self.vpc_id = None
        self.ig_id = None
        self.rt_id = None
        self.vpc_available = False
        self.ig_available = False
        self.rt_available = False
        self.vpc_resource = None


class DependenciesResolver(BaseVpcInit):
    def __init__(self):
        super().__init__()

    def validate(self):
        if self.vpc_id:
            if self.ig_id:
                if self.rt_id:
                    pass
                else:
                    print("Please launch internet gateway for launch the route table")
            else:
                print("Please launch internet gateway first ")
        else:
            print("Please Launch VPC first")


class Master(DependenciesResolver):
    """
    Launch and validate the vpc infrastructure using boto3.
    it inherits some methods and parameters from Availability class that will ensure
    the services are already launched or not if just create an instance of the class
    it just validate the vpc service is already exist or not.

    :type vpc_cidr: string
    :param vpc_cidr: cidr is required to Launch the vpc in that

    :type vpc_id: string
    :param vpc_id: its optional for already exist the vpc or not

    REFS = https://stackoverflow.com/questions/47329675/boto3-how-to-check-if-vpc-already-exists-before-creating-it
    :return: check the services already exist or not
    """
    def __init__(self, name=None, state=False, dry_run=False, region=None, cidr_block=None, route_table=None,
                 internet_gateway=None, *args, **kwargs):

        super().__init__()
        self.vpc = Vpc(vpc_name=name, state=state, dry_run=dry_run, vpc_cidr=cidr_block, region=region)
        self.ig = InternetGateway(
            name=internet_gateway.get('name', ''),
            state=internet_gateway.get('state', ''),
            dry_run=internet_gateway.get('dry_run', ''),
            region=internet_gateway.get('region', '')
        )
        self.rt = RouteTable(
            name=route_table.get('name', ''),
            state=route_table.get('state', ''),
            dry_run=route_table.get('dry_run', '')
        )

    def availability(self):
        try:
            _vpc_data: dict = self.vpc.validate()
            self.vpc_available = _vpc_data['available']
            self.vpc_id = _vpc_data['id']

            _ig_data: dict = self.ig.validate()
            self.ig_available = _ig_data['available']
            self.ig_id = _ig_data['id']

            _rt_data: dict = self.rt.validate()
            self.rt_available = _rt_data['available']
            self.rt_id = _rt_data['id']

        except Exception as e:
            print(f"Error during availability check: {e}")

    def create(self):
        super().validate()
        if not self.vpc_available:
            _vpc_data = self.vpc.create()
            self.vpc_id = _vpc_data['resource_id']
            print(_vpc_data)  # debug
        if not self.ig_available:
            _ig_data = self.ig.create(self.vpc_id)
            self.ig_id = _ig_data['resource_id']
            print(_ig_data)  # debug
        if not self.rt_available:
            self.rt.create(self.ig_id, self.vpc_id)


def runner(*args, **kwargs):
    for _vdata in kwargs['vpc']:
        master = Master(**_vdata)
        master.availability()
        master.create()


def run():
    runner(**config.model_dump())

