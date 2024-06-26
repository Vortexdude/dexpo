"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from dexpo.src.lib.models import RouteTable

REGION = 'ap-south-1'

extra_args = dict(
    resource_type='list',
)


class RouteTableInput(RouteTable):
    pass


module = DexpoModule(
    base_arg=RouteTableInput,
    extra_args=extra_args,
    module_type='route_tables'
)
logger = module.logger


class RouteTableManager:
    SERVICE = 'ec2'

    def __init__(self, rt_input: RouteTableInput):
        self.rt_input = rt_input
        self.ec2_client = boto3.client(self.SERVICE)
        self.ec2_resource = boto3.resource(self.SERVICE)

    def validate(self) -> dict:
        response = self.ec2_client.describe_route_tables(Filters=[{
            "Name": "tag:Name",
            "Values": [self.rt_input.name]
        }])
        if not response['RouteTables']:
            return {}
        else:
            return response['RouteTables'][0]

    def create(self, vpc_resource, ig_id: str):
        if self.rt_input.deploy:
            routeTable = vpc_resource.create_route_table()
            routeTable.create_tags(Tags=[{
                "Key": "Name",
                "Value": self.rt_input.name
            }])
            rt_id = str(routeTable.id)
            if ig_id:
                routeTable.create_route(
                    DestinationCidrBlock="0.0.0.0/0",
                    GatewayId=ig_id
                )

                logger.info(f"Public Route Table {self.rt_input.name} Created Successfully!")
            else:
                logger.info(f"Private Route Table {self.rt_input.name} Created Successfully!")
            return self.validate()

    def delete(self, rt_resource):
        rt_resource.delete()
        logger.info(f"Route Table {self.rt_input.name} deleted successfully")


def _validate_route_table(rt: RouteTableManager):
    logger.debug("Validating Route Table...")
    response = rt.validate()

    if module.validate_resource('RouteTableId', response):
        return

    module.save_state(response)


def _create_route_table(rt: RouteTableManager):
    logger.debug("Creating Route Table........")
    ig_id = None
    state_container = module.get_state()
    # check if the state having the RouteTableId key
    for vpc_entry in state_container.get('vpcs', []):
        index = module.extra_args['index']
        if vpc_entry.get('route_tables', [])[index].get('RouteTableId'):
            logger.info('Route Table already exist')
            return

    vpc_id = module.get_resource_values(
        vpc_resource='route_tables',
        resource_name=rt.rt_input.name,
        request='VpcId',
    )
    vpc_resource = boto3.resource('ec2').Vpc(vpc_id)
    if rt.rt_input.DestinationCidrBlock:
        ig_id = module.get_resource_values(
            vpc_resource='route_tables',
            resource_name=rt.rt_input.name,
            request='InternetGatewayId',
        )

    response = rt.create(vpc_resource, ig_id=ig_id)
    if response:
        module.save_state(response)


def _delete_route_table(rt: RouteTableManager):
    logger.debug("Deleting Route Table........")
    state_container = module.get_state()
    for vpc_entry in state_container.get('vpcs', []):
        index = module.extra_args['index']
        route_table = vpc_entry.get('route_tables')[index]
        if route_table.get('name') == rt.rt_input.name:
            if 'RouteTableId' in route_table:
                rt_id = route_table['RouteTableId']
                rt_resource = boto3.resource('ec2').RouteTable(rt_id)
                rt.delete(rt_resource)
                module.update_state(data=rt.rt_input.model_dump())
            else:
                logger.warn("Route Table is Not Launched Yet...")


def run_module(action: str, data: dict, *args, **kwargs):
    if 'index' not in kwargs:
        return

    module.extra_args['index'] = kwargs['index']
    inp = RouteTableInput(**data)
    rt = RouteTableManager(inp)

    if action == 'validate':
        return _validate_route_table(rt)

    elif action == 'create':
        return _create_route_table(rt)

    elif action == 'delete':
        return _delete_route_table(rt)
