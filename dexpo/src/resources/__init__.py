from .vpc.vpc import vpc_validator, create_vpc
from .vpc.route_table import route_table_validator, create_route_table
from .vpc.ig import internet_gateway_validator, create_internet_gateway
from .vpc.subnet import subnet_validator, create_subnet
from .vpc.security_group import security_group_validator, create_security_group
from dexpo.src.lib.utils import save_to_file, load_json


class ResourceManager:
    def __init__(self):
        self.data = {}

    @staticmethod
    def formatter(name, _id, resource):
        return {name: {"id": _id, 'resource': resource}}


rm = ResourceManager()


class ValidateHandler:
    def __init__(self, vpc_data):
        self.vpc_data: dict = vpc_data
        self.cloud_state = self.vpc_data.copy()
        self.vpc: dict = self.vpc_data['vpc']
        self.route_tables: list = self.vpc_data['route_tables']
        self.internet_gateway: dict = self.vpc_data['internet_gateway']
        self.subnets: list = self.vpc_data['subnets']
        self.security_groups: list = self.vpc_data['security_groups']
        self.validate()

    def validate(self):
        if 'name' in self.vpc:
            self.v_vpc()

        if any('name' in item for item in self.route_tables):
            self.resource_validator(
                data=self.route_tables,
                validator_func=route_table_validator,
                resource_key='rt'
            )

        if 'name' in self.internet_gateway:
            self.v_internet_gateway()

        if any('name' in item for item in self.subnets):
            self.resource_validator(
                data=self.subnets,
                validator_func=subnet_validator,
                resource_key='sn'
            )
        if any('name' in item for item in self.security_groups):
            self.resource_validator(
                data=self.security_groups,
                validator_func=security_group_validator,
                resource_key='sg'
            )

    @staticmethod
    def extractor(module_data):
        resource = module_data['resource']
        _id: str = ''
        if 'VpcId' in module_data:
            _id = module_data['VpcId']

        if 'InternetGatewayId' in module_data:
            _id = module_data['InternetGatewayId']

        if 'RouteTableId' in module_data:
            _id = module_data['RouteTableId']

        if 'SubnetId' in module_data:
            _id = module_data['SubnetId']

        if 'GroupId' in module_data:
            _id = module_data['GroupId']

        return _id, resource

    def _global_validator(self, data, validator_function) -> tuple[dict, dict]:
        module_resource_data = validator_function(data)
        if not module_resource_data:
            return {}, {}

        _id, _resource = self.extractor(module_resource_data)
        _resource_formatted_data = rm.formatter(name=data['name'], _id=_id, resource=_resource)
        del module_resource_data['resource']
        return module_resource_data, _resource_formatted_data

    def v_vpc(self):
        module_data, rm_vpc_data = self._global_validator(self.vpc, vpc_validator)
        rm.data.update({'vpc': rm_vpc_data})
        self.vpc.update(module_data)

    def v_internet_gateway(self):
        module_data, rm_ig_data = self._global_validator(self.internet_gateway, internet_gateway_validator)
        rm.data.update({'ig': rm_ig_data})
        self.internet_gateway.update(module_data)

    def resource_validator(self, data: list, validator_func, resource_key):
        resource_data = {}
        for index, rs_data in enumerate(data):
            module_data, _rm_data = self._global_validator(rs_data, validator_func)
            resource_data.update(_rm_data)
            data[index].update(module_data)
        rm.data.update({resource_key: resource_data})


class DeployHandler:
    def __init__(self, data):
        # {
        #     'data': {
        #             'vpc': {
        #                 'boto3-testing': {
        #                     'id': 'vpc-004a2319d98ed2714',
        #                     'resource': ec2.Vpc(id='vpc-004a2319d98ed2714')
        #                 }
        #             },
        #             'rt': {},
        #             'ig': {},
        #             'sn': {},
        #             'sg': {}
        #      }
        # }

        self.data = data
        self.cloud_state: dict = self.data.copy()
        self.vpc: dict = self.data['vpc']
        self.route_tables: list = self.data['route_tables']
        self.internet_gateway: dict = self.data['internet_gateway']
        self.subnets: list = self.data['subnets']
        self.security_groups: list = self.data['security_groups']
        self.vpc_resource: object = None
        self.internet_gateway_resource: object = None
        self.route_table_resource: object = None
        self.subnet_resource: object = None
        self.vpc_id: str = ''
        self.internet_gateway_id: str = ''
        self.route_table_id: str = ''
        self.subnet_id: str = ''

    @staticmethod
    def store_state(resource_type: str, resource_name: str, resource_id: str, boto_resource):
        rm.data.update({resource_type: rm.formatter(_id=resource_id, resource=boto_resource, name=resource_name)})

    @staticmethod
    def store_list_type_state(resource_type: str, data: dict):
        rm.data.update({resource_type: data})

    def launch(self):
        if 'VpcId' not in self.vpc:
            self.x_vpc()

        if 'InternetGatewayId' not in self.internet_gateway:
            self.x_ig()

        self.list_wrapper(self.route_tables, 'RouteTableId', 'rt', self.x_rt)
        self.list_wrapper(self.subnets, 'SubnetId', 'sb', self.x_sb)
        self.list_wrapper(self.security_groups, 'GroupId', 'sg', self.x_sg)

    def list_wrapper(self, resource_list: list, identifier: str, resource_type: str, function):
        global_resource_data = {}
        for resource in resource_list:
            if identifier not in resource:
                _resource_data = function(data=resource)
                global_resource_data.update(_resource_data)
        if global_resource_data != {}:
            self.store_list_type_state(resource_type=resource_type, data=global_resource_data)

    def x_vpc(self):
        vpc_name = self.vpc['name']
        print("Creating VPC " + vpc_name)
        response, vpc_resource = create_vpc(self.vpc)
        vpc_id = response['Vpc']['VpcId']  # response from the create method
        self.store_state(resource_id=vpc_id, resource_type='vpc', resource_name=vpc_name, boto_resource=vpc_resource)
        self.vpc.update(response)

    def x_ig(self):
        ig_name = self.internet_gateway['name']
        print("Creating Internet Gateway " + ig_name)
        vpc_resource = rm.data['vpc'][self.vpc['name']]['resource']  # get the vpc resource from resource manager
        response, ig_resource = create_internet_gateway(
            data=self.internet_gateway, vpc_resource=vpc_resource
        )
        ig_id = response['InternetGateway']['InternetGatewayId']
        self.store_state(resource_name=ig_name, resource_type='ig', resource_id=ig_id, boto_resource=ig_resource)
        self.internet_gateway.update(response)

    def x_rt(self, data):
        print("Creating Route Table " + data['name'])
        if not data['DestinationCidrBlock']:  # check for private route that doesn't have the public route
            self.internet_gateway_id = ''

        vpc_resource = rm.data['vpc'][self.vpc['name']]['resource']
        ig_id = rm.data['ig'][self.internet_gateway['name']]['id']
        rt_id, rt_resource = create_route_table(
            data=data, vpc_resource=vpc_resource, ig_id=ig_id
        )
        return rm.formatter(name=data['name'], _id=rt_id, resource=rt_resource)

    def x_sb(self, data):
        print("Creating Subnet " + data['name'])
        rt_resource = rm.data['rt'][data['route_table']]['resource']
        self.subnet_id, self.subnet_resource = create_subnet(
            data=data, vpc_resource=rm.data['vpc'][self.vpc['name']]['resource'], rt_resource=rt_resource
        )
        return rm.formatter(name=data['name'], _id=self.subnet_id, resource=self.subnet_resource)

    def x_sg(self, data):
        print("Creating security Group " + data['name'])
        sg_id, sg_resource = create_security_group(data, self.vpc_id)
        return rm.formatter(name=data['name'], _id=sg_id, resource=sg_resource)


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}
        self.state_file = 'state.json'

    @staticmethod
    def store_state(file='state.json', data=None):
        save_to_file(file, {"vpcs": data})

    def validate(self):
        _vpsStates = []
        for vpc_data in self.data['vpcs']:
            ValidateHandler(vpc_data)
            _vpsStates.append(vpc_data)
        self.store_state(data=_vpsStates)

    def apply(self):
        data = load_json(self.state_file)
        for vpc_data in data['vpcs']:
            dh = DeployHandler(data=vpc_data)
            dh.launch()

    def destroy(self):
        print('destroying...')
