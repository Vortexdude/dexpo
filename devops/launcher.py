import settings
from devops.models.config import RootModel
from devops.resources import Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
from devops.resources.vpc.security_group import SecurityGroup
from devops.lib.utils import Utils, DexColors
from settings import logger

dex_color = DexColors()

COMMAND = ''
RESOURCE_COUNT: int = 0


class VpcMaster(Base):
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
            vpc: dict = None,
            route_tables: dict = None,
            internet_gateway: dict = None,
            subnets: list[dict] = None,
            security_groups: list[dict] = None,
            *args, **kwargs):

        super().__init__(region='ap-south-1')
        self.security_groups = security_groups
        self.internet_gateway = internet_gateway
        self.subnets = subnets
        self.route_tables = route_tables
        self.vpc = vpc
        self.moduleStates = {}
        """Validating the VPC"""

        self.moduleVpc = Vpc(**vpc)
        self.moduleVpc.validate()
        _vpc_data = self.moduleVpc.to_dict(vpc)
        _vpc_data['object'] = self.moduleVpc
        self.moduleStates.update({self.vpc['name']: _vpc_data})

        """Validating the Internet Gateway"""

        self.moduleIg = InternetGateway(**internet_gateway)
        self.moduleIg.validate()
        _ig_data = self.moduleIg.to_dict(internet_gateway)
        _ig_data['object'] = self.moduleIg
        self.moduleStates.update({self.internet_gateway['name']: _ig_data})

        """Validating the route table"""

        for route_table in self.route_tables:
            self.moduleRt = RouteTable(**route_table)
            self.moduleRt.validate()
            _rt_data = self.moduleRt.to_dict(route_table)
            _rt_data['object'] = self.moduleRt
            self.moduleStates.update({route_table['name']: _rt_data})

        """Validating the Subnets"""

        for subnet in subnets:
            self.moduleSbn = Subnet(**subnet)
            self.moduleSbn.validate()
            _sb_data = self.moduleSbn.to_dict(subnet)
            _sb_data['object'] = self.moduleSbn
            self.moduleStates.update({subnet['name']: _sb_data})

        """Validating Security Group"""

        for security_group in security_groups:
            self.moduleSg = SecurityGroup(**security_group)
            self.moduleSg.validate()
            _sg_data = self.moduleSg.to_dict(security_group)
            _sg_data['object'] = self.moduleSg
            self.moduleStates.update({security_group['name']: _sg_data})

        # state_data = self.moduleStates.copy()

        # for k, v in state_data.items():
        #     del v['object']
        #
        # settings.store_state(data=state_data)

    def launch(self):
        for module_name, data in self.moduleStates.items():
            if not data['available']:
                if data['type'] == 'vpc':
                    self._create_vpc(module_name)

                if data['type'] == 'ig':
                    self._create_internet_gateway(module_name)

                if data['type'] == 'rt':
                    self._create_route_tables(module_name, data)

                if data['type'] == 'sb':
                    self._create_subnets(module_name, data)

                if data['type'] == 'sg':
                    self._create_security_groups(module_name, data)

    def _create_vpc(self, module_name):
        _vpc_data = self.moduleVpc.create()
        self._update_state(module_name, _vpc_data)

    def _create_internet_gateway(self, module_name):
        _ig_data = self.moduleIg.create(
            vpc_resource=self.moduleStates[self.vpc['name']]['resource']
        )
        self._update_state(module_name, _ig_data)

    def _create_route_tables(self, module_name: str, data: dict):

        for route_table in self.route_tables:
            gateway_id = ''
            if route_table['DestinationCidrBlock']:
                gateway_id = self.moduleStates[self.internet_gateway['name']]['id']

            if route_table['name'] == module_name:
                _rt_data = data['object'].create(
                    vpc_resource=self.moduleStates[self.vpc['name']]['resource'],
                    internet_gateway_id=gateway_id
                )
                self._update_state(module_name, _rt_data)

    def _create_subnets(self, module_name: str, data: dict):
        for subnet in self.subnets:
            if subnet['name'] == module_name:
                route_table_name = subnet['route_table']
                _sb_data = data['object'].create(
                    vpc_resource=self.moduleStates[self.vpc['name']]['resource'],
                    rt_resouce=self.moduleStates[route_table_name]['resource']
                )
                self._update_state(module_name, _sb_data)

    def _create_security_groups(self, module_name, data):
        for security_group in self.security_groups:
            if security_group['name'] == module_name:
                _sg_data = data['object'].create(
                    vpc_id=self.moduleStates[self.vpc['name']]['id']
                )
                self._update_state(module_name, _sg_data)

    def _update_state(self, module_name, new_data):
        self.moduleStates[module_name]['id'] = new_data['resource_id']
        self.moduleStates[module_name]['available'] = new_data['status']
        self.moduleStates[module_name]['resource'] = new_data['resource']


    def delete(self):
        """For delete the AWS resources Sequentially"""
        pass


def runner(action):
    vpcs = settings.vpcs
    for _vdata in vpcs:
        vpc_master = VpcMaster(**_vdata)
        if action.lower() == 'apply':
            vpc_master.launch()

        elif action.lower() == 'destroy':
            vpc_master.delete()


def run(command: str):
    runner(action=command)
