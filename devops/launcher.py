import boto3
from devops.models.config import RootModel
from devops.resources.vpc import Resources, Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
from devops.resources.vpc.security_group import SecurityGroup
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
            security_groups: list[dict] = None,
            *args, **kwargs):

        super().__init__()
        super(Base, self).__init__()
        self._subnets_availability = []
        self.subnets = subnets
        self.security_groups = security_groups

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

        """Validating the Subnets"""

        self.subnets_data = []
        for subnet in self.subnets:
            self._sb = Subnet(
                name=subnet['name'],
                state=subnet['state'],
                dry_run=subnet['dry_run'],
                subnet_cidr=subnet['cidr'],
            )
            _sb_data = self._sb.validate()
            print(_sb_data['message'])
            if _sb_data['available']:
                sb_id = _sb_data['id']
                sb_resource = _sb_data['resource']
            else:
                sb_resource = None
                sb_id = ""
            self.subnets_data.append({subnet['name']: [sb_resource, sb_id], "handler": self._sb})

        """Validating Security Group"""
        self.security_group_data = []
        for security_group in self.security_groups:
            self._sg = SecurityGroup(**security_group)
            _sg_data = self._sg.validate()
            print(_sg_data['message'])
            if _sg_data['available']:
                sg_id = _sg_data['id']
                sg_resource = _sg_data['resource']
            else:
                sg_id = _sg_data['id']
                sg_resource = _sg_data['resource']
            self.security_group_data.append({security_group['name']: [sg_resource, sg_id], "handler": self._sg})

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

        # going through the subnet validate data loop (form validate method) that contains
        # the status and resource of the subnet
        # then check availability of the subnet is there or not if not then create it
        _tmp_data = []
        for i in range(len(self.subnets_data)):
            if not self.subnets_data[i][self.subnets[i]['name']][0]:
                sb_data = self.subnets_data[i]["handler"].create(self.vpc_resource, self.rt_resource)
                print(sb_data['message'])
                _tmp_data.append({self.subnets[i]['name']: [sb_data['resource'], sb_data['resource_id']]})

        for i in range(len(self.security_group_data)):
            if not self.security_group_data[i][self.security_groups[i]['name']][0]:
                sg_data = self.security_group_data[i]["handler"].create(self.vpc_id)
                print(sg_data['message'])


def runner(*args, **kwargs):
    for _vdata in kwargs['vpc']:
        master = Master(**_vdata)
        master.launch()


def run():
    runner(**config.model_dump())
    # print(_json)
