"""These are docstrings basically a documentation of the module"""

import boto3
from dexpo.manager import DexpoModule
from pydantic import BaseModel
from typing import Optional

REGION = 'ap-south-1'

extra_args = dict(
    resource_type='list',
)


class RouteTableInput(BaseModel):
    name: str
    deploy: bool
    DestinationCidrBlock: Optional[str] = None


module = DexpoModule(
    base_arg=RouteTableInput,
    extra_args=extra_args,
    module_type='route_tables'
)
logger = module.logger


class RouteTableManager:
    def __init__(self, rt_input: RouteTableInput):
        self.rt_input = rt_input
        self.ec2_client = boto3.client("ec2")
        self.ec2_resource = boto3.resource('ec2')

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

                logger.info(f"Route Table {self.rt_input.name} Created Successfully!")
            return self.validate()


def _validate_route_table(rt: RouteTableManager):
    print(f"Validating Route Table........")
    response = rt.validate()
    # _current_state = module.get_state()
    if not response:
        logger.info("No Route table found in the cloud.")


def get_resource_values(route_table_name, request):
    _current_state = module.get_state()
    for vpc_entry in _current_state.get('vpcs', []):
        for rt in vpc_entry.get('route_tables', []):
            if rt.get('name') == route_table_name:
                if request == 'VpcId':
                    return vpc_entry['vpc']['VpcId']
                elif request == 'InternetGatewayId':
                    return vpc_entry['internet_gateway']['InternetGatewayId']
                else:
                    return


def _create_route_table(rt: RouteTableManager):
    print(f"Creating Route Table........")
    vpc_id = get_resource_values(rt.rt_input.name, 'VpcId')
    vpc_resource = boto3.resource('ec2').Vpc(vpc_id)
    ig_id = get_resource_values(rt.rt_input.name, 'InternetGatewayId') if rt.rt_input.DestinationCidrBlock else None
    response = rt.create(vpc_resource, ig_id=ig_id)
    if response:
        module.save_state()
    print(response)


def _delete_route_table(rt: RouteTableManager):
    print(f"Deleting Route Table........")


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
