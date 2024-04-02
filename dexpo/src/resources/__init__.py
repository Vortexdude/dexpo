from .vpc.vpc import vpc_handler
from .vpc.route_table import route_table_handler
from .vpc.ig import internet_gateway_handler
from dexpo.src.lib.utils import save_to_file

class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump()

    def validate(self):
        rt_x = []
        vpc_x = []
        vpc_state = {}
        for vpc_data in self.data['vpcs']:
            vpc_state['vpc'] = vpc_handler(vpc_data['vpc'])
            for rt_data in vpc_data['route_tables']:
                rt_state = route_table_handler(rt_data)
                rt_x.append(rt_state)
            vpc_state['route_tables'] = rt_x

            ig_state = internet_gateway_handler(vpc_data['internet_gateway'])
            vpc_state['internet_gateway'] = ig_state
            vpc_x.append(vpc_state)
        # print({"vpcs": vpc_x})
        save_to_file("state.json", {"vpcs": vpc_x})

    def apply(self):
        print('applying...')

    def destroy(self):
        print('destroying...')
