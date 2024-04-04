from .vpc.vpc import vpc_validator, create_vpc
from .vpc.route_table import route_table_validator
from .vpc.ig import internet_gateway_validator
from .vpc.subnet import subnet_validator
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


resources = ResourceManager()


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}

    def validate(self):
        _vpsStates = []
        for vpc_data in self.data['vpcs']:
            module_vpc_data = vpc_validator(vpc_data['vpc'])
            if module_vpc_data:
                vpc_id = list(module_vpc_data.values())[0]['VpcId']
                resources.add_resource('VpcId', vpc_id)
                vpc_data['vpc'].update(vpc_validator(vpc_data['vpc']))

            for idx, rt_data in enumerate(vpc_data['route_tables']):
                module_rt_data = route_table_validator(rt_data)
                if module_rt_data:
                    vpc_data['route_tables'][idx].update(route_table_validator(rt_data))

            module_ig_data = internet_gateway_validator(vpc_data['internet_gateway'])
            if module_ig_data:
                ig_id = list(module_ig_data.values())[0]['InternetGatewayId']
                resources.add_resource('InternetGatewayId', ig_id)
                vpc_data['internet_gateway'].update(module_ig_data)

            for sbi, subnet_data in enumerate(vpc_data['subnets']):
                module_sb_data = subnet_validator(subnet_data)
                if module_sb_data:
                    vpc_data['subnets'][sbi].update(module_sb_data)

            for sgi, sg_data in enumerate(vpc_data['security_groups']):
                module_sg_data = security_group_validator(sg_data)
                if module_sg_data:
                    vpc_data['security_groups'][sgi].update(module_sg_data)

            _vpsStates.append(vpc_data)

        save_to_file("state.json", {"vpcs": _vpsStates})

    def apply(self):
        print(resources.__dict__)
        data = load_json('state.json')

        for vpc_data in data['vpcs']:
            vpc_name = vpc_data['vpc']['name']
            if vpc_name not in vpc_data['vpc']:
                print("Creating VPC " + vpc_name)
                # create_vpc(vpc_data['vpc'])

            for rt in vpc_data['route_tables']:
                rt_name = rt['name']
                if rt_name not in rt:
                    print("Creating Route Table " + rt_name)

            ig_name = vpc_data['internet_gateway']['name']
            if ig_name not in vpc_data['internet_gateway']:
                print("Creating Internet Gateway " + ig_name)

            for subnet in vpc_data['subnets']:
                sb_name = subnet['name']
                if sb_name not in subnet:
                    print("Creating Subnet " + sb_name)

            for sg in vpc_data['security_groups']:
                sg_name = sg['name']
                if sg_name not in sg:
                    print("Creating Subnet " + sg_name)

    def destroy(self):
        print('destroying...')
