from .vpc.vpc import vpc_validator
from .vpc.route_table import route_table_validator
from .vpc.ig import internet_gateway_validator
from .vpc.subnet import subnet_validator
from .vpc.security_group import security_group_validator
from dexpo.src.lib.utils import save_to_file


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump()

    def validate(self):
        rt_x = []
        vpc_x = []
        sb_x = []
        sg_x = []
        vpc_state = {}
        for vpc_data in self.data['vpcs']:
            vpc_state['vpc'] = vpc_validator(vpc_data['vpc'])
            for rt_data in vpc_data['route_tables']:
                rt_state = route_table_validator(rt_data)
                rt_x.append(rt_state)
            vpc_state['route_tables'] = rt_x

            ig_state = internet_gateway_validator(vpc_data['internet_gateway'])
            vpc_state['internet_gateway'] = ig_state
            vpc_x.append(vpc_state)

            for subnet_data in vpc_data['subnets']:
                subnet_state = subnet_validator(subnet_data)
                sb_x.append(subnet_state)
            vpc_state['subnets'] = sb_x

            for sg_data in vpc_data['security_groups']:
                sg_state = security_group_validator(sg_data)
                sg_x.append(sg_state)
            vpc_state['security_groups'] = sg_x

        save_to_file("state.json", {"vpcs": vpc_x})

    def apply(self):
        print('applying...')

    def destroy(self):
        print('destroying...')
