from dexpo.settings import logger
from dexpo.src.lib.state_management import state
from dexpo.src.resources.vpc.vpc import create_vpc
from dexpo.src.resources.vpc.ig import create_internet_gateway
from dexpo.src.resources.vpc.rt import create_route_table
from dexpo.src.resources.vpc.sb import create_subnet
from dexpo.src.resources.vpc.sg import create_sg


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
        self.vpc_name = self.vpc['name']
        self.route_tables: list = self.data['route_tables']
        self.internet_gateway: dict = self.data['internet_gateway']
        self.ig_name = self.internet_gateway['name']
        self.subnets: list = self.data['subnets']
        self.security_groups: list = self.data['security_groups']

    @staticmethod
    def store_state(resource_type: str, resource_name: str, resource_id: str, boto_resource):
        state.data.update({resource_type: state.formatter(_id=resource_id, resource=boto_resource, name=resource_name)})

    @staticmethod
    def store_list_type_state(resource_type: str, data: dict):
        state.data.update({resource_type: data})

    def get_data(self, resource):
        if 'vpc_id' in resource:
            return state.data['vpc'][self.vpc_name]['id']

        if 'vpc_resource' in resource:
            return state.data['vpc'][self.vpc_name]['resource']

        if 'ig_id' in resource:
            return state.data['ig'][self.internet_gateway['name']]['id']

        if 'ig_resource' in resource:
            return state.data['ig'][self.internet_gateway['name']]['resource']

        if 'rt_resource' in resource:
            return state.data['rt'][self.route_tables]['id']

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
        logger.info("Creating VPC " + self.vpc_name)
        response, vpc_resource = create_vpc(self.vpc)
        vpc_id = response['Vpc']['VpcId']  # response from the create method
        self.store_state(resource_id=vpc_id, resource_type='vpc', resource_name=self.vpc_name, boto_resource=vpc_resource)
        self.vpc.update(response)

    def x_ig(self):
        ig_name = self.internet_gateway['name']
        logger.info("Creating Internet Gateway " + ig_name)
        vpc_resource = self.get_data('vpc_resource')
        response, ig_resource = create_internet_gateway(
            data=self.internet_gateway, vpc_resource=vpc_resource
        )
        ig_id = response['InternetGateway']['InternetGatewayId']
        self.store_state(resource_name=ig_name, resource_type='ig', resource_id=ig_id, boto_resource=ig_resource)
        self.internet_gateway.update(response)

    def x_rt(self, data):
        logger.info("Creating Route Table " + data['name'])
        vpc_resource = self.get_data('vpc_resource')
        ig_id = self.get_data('ig_id')
        if not data['DestinationCidrBlock']:  # check for private route that doesn't have the public route
            ig_id = ''

        rt_id, rt_resource = create_route_table(
            data=data, vpc_resource=vpc_resource, ig_id=ig_id
        )
        return state.formatter(name=data['name'], _id=rt_id, resource=rt_resource)

    def x_sb(self, data):
        logger.info("Creating Subnet " + data['name'])
        rt_resource = state.data['rt'][data['route_table']]['resource']
        vpc_resource = self.get_data('vpc_resource')
        sb_id, sb_resource = create_subnet(
            data=data, vpc_resource=vpc_resource, rt_resource=rt_resource
        )
        return state.formatter(name=data['name'], _id=sb_id, resource=sb_resource)

    def x_sg(self, data):
        logger.info("Creating security Group " + data['name'])
        vpc_id = self.get_data('vpc_id')
        sg_id, sg_resource = create_sg(data, vpc_id)
        return state.formatter(name=data['name'], _id=sg_id, resource=sg_resource)
