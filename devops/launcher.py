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
            route_table: dict = None,
            internet_gateway: dict = None,
            subnets: list[dict] = None,
            security_groups: list[dict] = None,
            *args, **kwargs):

        super().__init__(region='ap-south-1')
        self.security_groups = security_groups
        self.internet_gateway = internet_gateway
        self.subnets = subnets
        self.route_table = route_table
        self.vpc = vpc
        self.moduleStates = {}
        """Validating the VPC"""

        self.moduleVpc = Vpc(**vpc)
        self.moduleVpc.validate()
        self.moduleStates.update({self.vpc['name']: self.moduleVpc.to_dict(vpc)})

        """Validating the Internet Gateway"""

        self.moduleIg = InternetGateway(**internet_gateway)
        self.moduleIg.validate()
        self.moduleStates.update({self.internet_gateway['name']: self.moduleIg.to_dict(internet_gateway)})

        """Validating the route table"""

        self.moduleRt = RouteTable(**route_table)
        self.moduleRt.validate()
        self.moduleStates.update({self.route_table['name']: self.moduleRt.to_dict(route_table)})

        """Validating the Subnets"""

        for subnet in subnets:
            self.moduleSbn = Subnet(**subnet)
            self.moduleSbn.validate()
            self.moduleStates.update({subnet['name']: self.moduleSbn.to_dict(subnet)})

        """Validating Security Group"""

        for security_group in security_groups:
            self.moduleSg = SecurityGroup(**security_group)
            self.moduleSg.validate()
            self.moduleStates.update({security_group['name']: self.moduleSg.to_dict(security_group)})

    def _store_state(self):
        settings.store_state(data=self.moduleStates)

    def launch(self):
        _resource_mapping = {
            'vpc': (self.vpc, self.moduleVpc),
            'ig': (self.internet_gateway, self.moduleIg),
            'sg': (self.security_groups, self.moduleSg),
            'sb': (self.subnets, self.moduleSbn),
            'rt': (self.route_table, self.moduleRt)
        }

        for module_name, data in self.moduleStates.items():

            if not data['available']:
                if data['type'] == 'vpc' and not data['available']:
                    _vpc_data = self.moduleVpc.create()

                    self.moduleStates[self.vpc['name']]['available'] = _vpc_data['status']
                    self.moduleStates[self.vpc['name']]['id'] = _vpc_data['resource_id']
                    self.moduleStates[self.vpc['name']]['resource'] = _vpc_data['resource']

                if self.moduleStates[self.vpc['name']]['available']:
                    if data['type'] == 'ig':
                        _ig_data = self.moduleIg.create(
                            vpc_resource=self.moduleStates[self.vpc['name']]['resource']
                        )
                        self.moduleStates[self.internet_gateway['name']]['available'] = _ig_data['status']
                        self.moduleStates[self.internet_gateway['name']]['id'] = _ig_data['resource_id']
                        self.moduleStates[self.internet_gateway['name']]['resource'] = _ig_data['resource']

                if data['type'] == 'rt':
                    _rt_data = self.moduleRt.create(
                        vpc_resource=self.moduleStates[self.vpc['name']]['resource'],
                        internet_gateway_id=self.moduleStates[self.internet_gateway['name']]['id']
                    )
                    self.moduleStates[self.route_table['name']]['available'] = _rt_data['status']
                    self.moduleStates[self.route_table['name']]['resource_id'] = _rt_data['resource_id']
                    self.moduleStates[self.route_table['name']]['resource'] = _rt_data['resource']

                if data['type'] == 'sb':
                    _sb_data = self.moduleSbn.create(
                        vpc_resource=self.moduleStates[self.vpc['name']]['resource'],
                        rt_resouce=self.moduleStates[self.route_table['name']]['resource']
                    )
                    print(f"{_sb_data = }")
                    self.moduleStates[module_name]['available'] = _sb_data['status']
                    self.moduleStates[module_name]['resource_id'] = _sb_data['resource_id']
                    self.moduleStates[module_name]['resource'] = _sb_data['resource']
            #
            #     if data['type'] == 'sg':
            #         # for security_group in self.security_groups:
            #         _sg_data = self.moduleSg.create(
            #             vpc_id=self.moduleStates[self.vpc['name']]['id']
            #         )
            #
            #         self.moduleStates[module_name]['available'] = _sg_data['status']
            #         self.moduleStates[module_name]['resource_id'] = _sg_data['resource_id']
            #         self.moduleStates[module_name]['resource'] = _sg_data['resource']

    def delete(self):
        """For delete the AWS resources Sequentially"""
        pass


def runner(action):
    vpcs = settings.vpcs
    for _vdata in vpcs:
        vpc_master = VpcMaster(**_vdata)
        if action.lower() == 'apply':
            vpc_master.launch()
            # pass
        elif action.lower() == 'destroy':
            vpc_master.delete()


def run(command: str):
    runner(action=command)
