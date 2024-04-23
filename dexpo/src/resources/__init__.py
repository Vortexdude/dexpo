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
    def formatter(name, id, resource):
        return {name: {"id": id, 'resource': resource}}


rm = ResourceManager()


class ValidatorClass:
    def __init__(self, vpc_data):
        self.vpc_data: dict = vpc_data
        self.cloud_state = self.vpc_data.copy()
        self.vpc: dict = self.vpc_data['vpc']
        self.route_tables: list = self.vpc_data['route_tables']
        self.internet_gateway: dict = self.vpc_data['internet_gateway']
        self.subnets: list = self.vpc_data['subnets']
        self.security_groups: list = self.vpc_data['security_groups']
        if 'name' in self.vpc:
            print("validating VPC . . .")
            self.v_vpc()
        if any('name' in item for item in self.route_tables):
            print("validating Route Tables . . .")
            self.v_route_tables()
        if 'name' in self.internet_gateway:
            print("validating Internet Gateway . . .")
            self.v_internet_gateway()
        if any('name' in item for item in self.subnets):
            print("validating subnets . . .")
            self.v_subnet()
        if any('name' in item for item in self.security_groups):
            print("validating security Groups . . .")
            self.v_security_group()

    @staticmethod
    def extractor(module_data):
        resource = module_data['resource']
        _id: str = ''
        if 'VpcId' in module_data:
            _id = module_data['VpcId']

        if 'RouteTableId' in module_data:
            _id = module_data['RouteTableId']

        if 'SubnetId' in module_data:
            _id = module_data['SubnetId']

        if 'GroupId' in module_data:
            _id = module_data['GroupId']

        return _id, resource

    def v_vpc(self):
        module_data, rm_vpc_data = self._global_validator(self.vpc, vpc_validator)
        rm.data.update({'vpc': rm_vpc_data})
        self.vpc.update(module_data)

    def v_route_tables(self):
        rm_route_table_data = {}
        for rt_index, rt_data in enumerate(self.route_tables):
            module_data, _rm_rt_data = self._global_validator(rt_data, route_table_validator)
            rm_route_table_data.update(_rm_rt_data)
            self.route_tables[rt_index].update(module_data)

        rm.data.update({'rt': rm_route_table_data})

    def _global_validator(self, data, validator_function) -> tuple[dict, dict]:
        module_resource_data = validator_function(data)
        if not module_resource_data:
            return {}, {}

        _id, _resource = self.extractor(module_resource_data)
        _resource_formatted_data = rm.formatter(name=data['name'], id=_id, resource=_resource)
        del module_resource_data['resource']
        return module_resource_data, _resource_formatted_data

    def v_internet_gateway(self):
        module_data, rm_ig_data = self._global_validator(self.internet_gateway, internet_gateway_validator)
        rm.data.update({'ig': rm_ig_data})
        self.internet_gateway.update(module_data)

    def v_subnet(self):
        subnet_data = {}
        for sb_index, sb_data in enumerate(self.subnets):
            module_data, _rm_sb_data = self._global_validator(sb_data, subnet_validator)
            self.subnets[sb_index].update(module_data)
        rm.data.update({'sb': subnet_data})

    def v_security_group(self):
        security_group_data = {}
        for sg_index, sg_data in enumerate(self.security_groups):
            module_data, _rm_sg_data = self._global_validator(sg_data, security_group_validator)
            self.security_groups[sg_index].update(module_data)
        rm.data.update({'sg': security_group_data})


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}

    @staticmethod
    def store_state(file='state.json', data=None):
        save_to_file(file, {"vpcs": data})

    def validate(self):
        _vpsStates = []
        for vpc_data in self.data['vpcs']:
            vvs = ValidatorClass(vpc_data)
            _vpsStates.append(vpc_data)

        self.store_state(data=_vpsStates)
        print(_vpsStates)

    def apply(self):
        pass
        # print(resourceMan.__dict__)
        # data = load_json('state.json')
        #
        # for vpc_data in data['vpcs']:
        #     vpc_name = vpc_data['vpc']['name']
        #     if 'VpcId' not in vpc_data['vpc']:
        #         print("Creating VPC " + vpc_name)
        #         vpc_id, vpc_resource = create_vpc(vpc_data['vpc'])
        #         resourceMan.add_resource('vpc', vpc_resource)
        #         resourceMan.add_resource('VpcId', vpc_id)
        #
        #     ig_name = vpc_data['internet_gateway']['name']
        #     if 'InternetGatewayId' not in vpc_data['internet_gateway']:
        #         print("Creating Internet Gateway " + ig_name)
        #         vpc_resource = resourceMan.resources['vpc']
        #         ig_id, ig_resource = create_internet_gateway(vpc_data['internet_gateway'], vpc_resource)
        #         resourceMan.add_resource('ig', ig_resource)
        #         resourceMan.add_resource('InternetGatewayId', ig_id)
        #
        #     route_table_data = {}
        #     for rt in vpc_data['route_tables']:
        #         if 'RouteTableId' not in rt:
        #             vpc_resource = resourceMan.resources['vpc']
        #             ig_id = resourceMan.resources['InternetGatewayId']
        #             print("Creating Route Table " + rt['name'])
        #             rt_id, rt_resource = create_route_table(rt, vpc_resource, ig_id)
        #             _rt_data = {'id': rt_id, 'resource': rt_resource}
        #             route_table_data.update({rt['name']: _rt_data})
        #     resourceMan.add_resource('rt', route_table_data)
        #
        #     subnet_data = {}
        #     for subnet in vpc_data['subnets']:
        #         if 'SubnetId' not in subnet:
        #             vpc_resource = resourceMan.resources['vpc']
        #             associate_route_table = subnet['route_table']
        #             rt_resource = resourceMan.resources['rt'][associate_route_table]['resource']
        #             print("Creating Subnet " + subnet['name'])
        #             sb_id, sb_resource = create_subnet(subnet, vpc_resource, rt_resource)
        #             _rt_data = {'id': sb_id, 'resource': sb_resource}
        #             subnet_data.update({subnet['name']: _rt_data})
        #     resourceMan.add_resource('sb', subnet_data)
        #
        #     security_group_data = {}
        #     for sg in vpc_data['security_groups']:
        #         if 'GroupId' not in sg:
        #             print("Creating Subnet " + sg['name'])
        #             vpc_id = resourceMan.resources['VpcId']
        #             sg_id, sg_resource = create_security_group(sg, vpc_id)
        #             _sg_data = {'id': sg_id, 'resource': sg_resource}
        #             security_group_data.update({sg['name']: _sg_data})
        #     resourceMan.add_resource('sg', security_group_data)

    def destroy(self):
        print('destroying...')
