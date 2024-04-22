from .vpc.vpc import vpc_validator, create_vpc
from .vpc.route_table import route_table_validator, create_route_table
from .vpc.ig import internet_gateway_validator, create_internet_gateway
from .vpc.subnet import subnet_validator, create_subnet
from .vpc.security_group import security_group_validator
from dexpo.src.lib.utils import save_to_file, load_json


class ResourceManager:
    def __init__(self):
        self.resources = {}

    def add_resource(self, key, resource):
        self.resources[key] = resource

    def get_resource(self, key):
        return self.resources.get(key)

    def remove_resource(self, key):
        if key in self.resources:
            del self.resources[key]

    def modify_resource(self, key, new_resource):
        if key in self.resources:
            self.resources[key] = new_resource


resourceMan = ResourceManager()


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}

    def validate(self):
        _vpsStates = []
        for vpc_data in self.data['vpcs']:
            module_vpc_data = vpc_validator(vpc_data['vpc'])
            if module_vpc_data:
                vpc_id = module_vpc_data['VpcId']
                vpc_resource = module_vpc_data['resource']
                resourceMan.add_resource('VpcId', vpc_id)
                resourceMan.add_resource('vpc', vpc_resource)
                del module_vpc_data['resource']
                vpc_data['vpc'].update(module_vpc_data)

            route_table_data = {}
            for rt_index, rt_data in enumerate(vpc_data['route_tables']):
                module_rt_data = route_table_validator(rt_data)
                if module_rt_data:
                    _rt_data = {'id': module_rt_data['RouteTableId'], 'resource': module_rt_data['resource']}
                    route_table_data.update({rt_data['name']: _rt_data})
                    vpc_data['route_tables'][rt_index].update(module_rt_data)
                    del vpc_data['route_tables'][rt_index]['resource']
            resourceMan.add_resource('rt', route_table_data)

            module_ig_data = internet_gateway_validator(vpc_data['internet_gateway'])
            if module_ig_data:
                ig_id = module_ig_data['InternetGatewayId']
                resourceMan.add_resource('InternetGatewayId', ig_id)
                resourceMan.add_resource('ig', module_ig_data['resource'])
                del module_ig_data['resource']
                vpc_data['internet_gateway'].update(module_ig_data)
                # here we use 0 because we are using only one internet gateway per vpc
                # but we will find lots of it during the validate command

            subnet_data = {}
            for sb_index, sb_data in enumerate(vpc_data['subnets']):
                module_sb_data = subnet_validator(sb_data)
                if module_sb_data:
                    _sb_data = {'id': module_sb_data['SubnetId'], 'resource': module_sb_data['resource']}
                    subnet_data.update({sb_data['name']: _sb_data})
                    del module_sb_data['resource']
                    vpc_data['subnets'][sb_index].update(module_sb_data)

            resourceMan.add_resource('sb', subnet_data)

            for sgi, sg_data in enumerate(vpc_data['security_groups']):
                module_sg_data = security_group_validator(sg_data)
                if module_sg_data:
                    vpc_data['security_groups'][sgi].update(module_sg_data)

            _vpsStates.append(vpc_data)
        # print(_vpsStates)
        save_to_file("state.json", {"vpcs": _vpsStates})

    def apply(self):
        print(resourceMan.__dict__)
        data = load_json('state.json')

        for vpc_data in data['vpcs']:
            vpc_name = vpc_data['vpc']['name']
            if 'VpcId' not in vpc_data['vpc']:
                print("Creating VPC " + vpc_name)
                vpc_id, vpc_resource = create_vpc(vpc_data['vpc'])
                resourceMan.add_resource('vpc', vpc_resource)
                resourceMan.add_resource('VpcId', vpc_id)

            ig_name = vpc_data['internet_gateway']['name']
            if 'InternetGatewayId' not in vpc_data['internet_gateway']:
                print("Creating Internet Gateway " + ig_name)
                vpc_resource = resourceMan.resources['vpc']
                ig_id, ig_resource = create_internet_gateway(vpc_data['internet_gateway'], vpc_resource)
                resourceMan.add_resource('ig', ig_resource)
                resourceMan.add_resource('InternetGatewayId', ig_id)

            route_table_data = {}
            for rt in vpc_data['route_tables']:
                if 'RouteTableId' not in rt:
                    vpc_resource = resourceMan.resources['vpc']
                    ig_id = resourceMan.resources['InternetGatewayId']
                    print("Creating Route Table " + rt['name'])
                    rt_id, rt_resource = create_route_table(rt, vpc_resource, ig_id)
                    _rt_data = {'id': rt_id, 'resource': rt_resource}
                    route_table_data.update({rt['name']: _rt_data})
            resourceMan.add_resource('rt', route_table_data)

            for subnet in vpc_data['subnets']:
                if 'SubnetId' not in subnet:
                    vpc_resource = resourceMan.resources['vpc']
                    associate_route_table = subnet['route_table']
                    rt_resource = resourceMan.resources['rt'][associate_route_table]['resource']
                    print("Creating Subnet " + subnet['name'])
                    sb_id, sb_resource = create_subnet(subnet, vpc_resource, rt_resource)

            for sg in vpc_data['security_groups']:
                sg_name = sg['name']
                if sg_name not in sg:
                    print("Creating Subnet " + sg_name)

    def destroy(self):
        print('destroying...')
