import logging

import settings
from devops.resources import Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
from devops.resources.vpc.security_group import SecurityGroup
from devops.resources.ec2 import Ec2
from settings import logger

COMMAND = ''
RESOURCE_COUNT: int = 0


class Ec2Master(Base):
    def __init__(self,
                 moduleStates: dict = None,
                 region: str = 'ap-south-1',
                 ec2: dict = None,
                 ):
        super().__init__(region)
        self.ec2 = ec2
        self.moduleEc2 = None
        self.moduleStates = moduleStates
        # print(self.moduleStates)
        self.validate()

    def validate(self):
        """Validating the EC2 """

        if self.ec2['vpc'] in self.moduleStates:
            if self.moduleStates[self.ec2['vpc']]['available']:
                self.moduleEc2 = Ec2(**self.ec2)
                self.moduleEc2.validate()
                _ec2_data = self.moduleEc2.to_dict(self.ec2)
                _ec2_data['object'] = self.moduleEc2
                self.moduleStates.update({self.ec2['name']: _ec2_data})

            else:
                logger.warn("Vpc is not available")

        else:
            logger.warn("This vpc in not in defined state")

    def to_dict(self):
        return self.moduleStates

    def launch(self):
        security_groups_id = []
        for sg in self.ec2['security_groups']:
            security_groups_id.append(self.moduleStates[sg]['id'])

        if not self.moduleStates[self.ec2['name']]['available']:
            self.moduleStates[self.ec2['name']]['object'].create(
                subnet_id=self.moduleStates[self.ec2['subnet']]['id'],
                security_group_ids=security_groups_id
            )

    def delete(self):
        pass


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
            ec2s: dict = None,
            *args, **kwargs):

        super().__init__(region='ap-south-1')
        self.security_groups = security_groups
        self.internet_gateway = internet_gateway
        self.subnets = subnets
        self.route_tables = route_tables
        self.ec2s = ec2s
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
        create_resources = {
            'vpc': self._create_vpc,
            'ig': self._create_internet_gateway,
            'rt': self._create_route_tables,
            'sb': self._create_subnets,
            'sg': self._create_security_groups,
        }
        for module_name, data in self.moduleStates.items():
            """Check every resource is available or not
            call the data['type'] from the dict see above |^
            example = data['type'] = 'vpc', 'ig', 'rt'
            """

            if not data['available'] and data['type'] in create_resources:
                create_resource = create_resources[data['type']]
                create_resource(module_name, data)

    def _create_vpc(self, module_name: str, data: dict = None):
        _vpc_data = data['object'].create()
        self._update_state(module_name, _vpc_data)

    def _create_internet_gateway(self, module_name: str, data: dict = None):
        _ig_data = data['object'].create(
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
        vpc_resources = []
        subnet_resources = []
        route_table_resources = []
        security_group_resources = []
        internet_gateway_resources = []

        for module_name, data in self.moduleStates.items():
            if data['type'] == 'ig':
                internet_gateway_resources.append(data)
            if data['type'] == 'vpc':
                vpc_resources.append(data)
            elif data['type'] == 'sb':
                subnet_resources.append(data)
            elif data['type'] == 'rt':
                route_table_resources.append(data)
            elif data['type'] == 'sg':
                security_group_resources.append(data)

        # """ Delete the resources in the order """
        for internet_gateway_resource in internet_gateway_resources:
            internet_gateway_resource['object'].delete(
                vpc_resource=self.moduleStates[self.vpc['name']]['resource'],
                vpc_id=self.moduleStates[self.vpc['name']]['id'],
            )

        for subnet_data in subnet_resources:
            subnet_data['object'].delete(
                sb_resource=subnet_data['resource']
            )

        for route_table_data in route_table_resources:
            route_table_data['object'].delete(
                rt_resource=route_table_data['resource']
            )

        for security_group_data in security_group_resources:
            security_group_data['object'].delete(
                sg_resource=security_group_data['resource']
            )

        for vpc_data in vpc_resources:
            vpc_data['object'].delete()


def runner(action):
    global vpc_master
    from devops.resources.ec2 import Ec2
    vpcs = settings.vpcs
    ec2s = settings.ec2s
    for _vdata in vpcs:
        vpc_master = VpcMaster(**_vdata)
        if action.lower() == 'apply':
            vpc_master.launch()

        elif action.lower() == 'destroy':
            vpc_master.delete()

    for ec2 in ec2s:
        ec2_master = Ec2Master(moduleStates=vpc_master.moduleStates, ec2=ec2,)
        vpc_master.moduleStates = ec2_master.to_dict()
        if action.lower() == 'apply':
            ec2_master.launch()

        if action.lower() == 'destroy':
            ec2_master.delete()

        # print(vpc_master.moduleStates)


def run(command: str):
    runner(action=command)
