from .vpc.vpc import VpcResource
from .vpc.route_table import RouteTable
from .vpc.ig import InternetGateway
from dexpo.src.resources.main import State

vpc_state = State()


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump()

    def validate(self):
        for vpc_data in self.data['vpcs']:
            vpc_obj = VpcResource(**vpc_data['vpc'])
            vpcs = vpc_obj.validate()
            if not vpcs:
                print("No Vpc found under the name and CIDR block")
                #  Handle the exiting or skipping form here
            for vpc in vpcs:
                vpc_state.add_resource(vpc['VpcId'], vpc)

            for rt_data in vpc_data['route_tables']:
                rt_obj = RouteTable(**rt_data)
                rts = rt_obj.validate()
                if not rts:
                    print("No Route Table found under the Name tag " + rt_data['name'])
                    #  Handle the exiting or skipping form here
                for rt in rts:
                    vpc_state.add_resource(rt['RouteTableId'], rt)

            ig_obj = InternetGateway(**vpc_data['internet_gateway'])
            igs = ig_obj.validate()
            if not igs:
                print("No Internet Gateway found under the Name tag " + vpc_data['internet_gateway']['name'])
            print(igs)

            # vpc_state.save_to_file('state.json')

    def apply(self):
        print('applying...')

    def destroy(self):
        print('destroying...')
