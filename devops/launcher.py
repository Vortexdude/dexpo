import boto3
from devops.models.config import RootModel
from devops.resources.vpc import Resources, Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
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


class Master(BaseVpcInit, Base):
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

    def __init__(
            self,
            name: str = None,
            state: str = False,
            dry_run: bool = False,
            region: str = None,
            cidr_block: str = None,
            route_table: dict = None,
            internet_gateway: dict = None,
            subnets: list[dict] = None,
            *args, **kwargs):

        super().__init__()
        super(Base, self).__init__()
        self._subnets_availability = []
        self.subnets = subnets

        """Validating the VPC"""

        self._vpc = Vpc(vpc_name=name, state=state, dry_run=dry_run, vpc_cidr=cidr_block, region=region)
        self._vpc_data = self._vpc.validate()
        print(self._vpc_data['message'])
        if self._vpc_data['available']:
            self.vpc_id = self._vpc_data['id']
            self.vpc_resource = self._vpc_data['resource']
        else:
            self.vpc_resource = None
            self.vpc_id = ''

        """Validating the Internet Gateway"""

        self._ig = InternetGateway(
            name=internet_gateway.get('name', ''),
            state=internet_gateway.get('state', ''),
            dry_run=internet_gateway.get('dry_run', ''),
            region=internet_gateway.get('region', '')
        )
        self._ig_data = self._ig.validate()
        print(self._ig_data['message'])
        if self._ig_data['available']:
            self.ig_id = self._ig_data['id']
            self.ig_resource = self._ig_data['resource']
        else:
            self.ig_resource = None
            self.ig_id = ""

        """Validating the route table"""

        self._rt = RouteTable(
            name=route_table.get('name', ''),
            state=route_table.get('state', ''),
            dry_run=route_table.get('dry_run', '')
        )
        self._rt_data = self._rt.validate()
        print(self._rt_data['message'])
        if self._rt_data['available']:
            self.rt_id = self._rt_data['id']
            self.rt_resource = self._rt_data['resource']
        else:
            self.rt_resource = None
            self.rt_id = ""

    def launch(self):
        if not self._vpc_data['available']:
            self._vpc_data = self._vpc.create()
            print(self._vpc_data['message'])
            if self._vpc_data['status']:
                self.vpc_resource = self._vpc_data['resource']
                self.vpc_id = self._vpc_data['resource_id']

        if not self._ig_data['available']:
            self._ig_data = self._ig.create(self.vpc_resource)
            print(self._ig_data['message'])
            if self._ig_data['status']:
                self.ig_resource = self._ig_data['resource']
                self.ig_id = self._ig_data['resource_id']

        if not self._rt_data['available']:
            self._rt_data = self._rt.create(self.vpc_resource, self.ig_id)
            print(self._rt_data['message'])
            if self._rt_data['status']:
                self.rt_resource = self._rt_data['resource']
                self.rt_id = self._rt_data['resource_id']

def runner(*args, **kwargs):
    for _vdata in kwargs['vpc']:
        master = Master(**_vdata)
        master.launch()


def run():
    runner(**config.model_dump())
    # print(_json)
