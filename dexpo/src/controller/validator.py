from dexpo.settings import logger
from dexpo.src.lib.state_management import state
from dexpo.src.resources.vpc.vpc import vpc_validator
from dexpo.src.resources.vpc.ig import internet_gateway_validator
from dexpo.src.resources.vpc.route_table import route_table_validator
from dexpo.src.resources.vpc.subnet import subnet_validator
from dexpo.src.resources.vpc.security_group import security_group_validator
from dexpo.src.controller.main import dexpo

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
            logger.debug("validating VPC")
            self.v_vpc()

        if any('name' in item for item in self.route_tables):
            logger.debug("validating RouteTables")
            self.resource_validator(
                data=self.route_tables,
                validator_func=route_table_validator,
                resource_key='rt'
            )

        if 'name' in self.internet_gateway:
            logger.debug("validating Internet Gateway")
            self.v_internet_gateway()

        if any('name' in item for item in self.subnets):
            logger.debug("validating Subnets")
            self.resource_validator(
                data=self.subnets,
                validator_func=subnet_validator,
                resource_key='sn'
            )
        if any('name' in item for item in self.security_groups):
            logger.debug("validating Security Groups")
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
        _resource_formatted_data = state.formatter(name=data['name'], _id=_id, resource=_resource)
        del module_resource_data['resource']
        return module_resource_data, _resource_formatted_data

    def v_vpc(self):
        module_data, rm_vpc_data = self._global_validator(self.vpc, vpc_validator)
        state.data.update({'vpc': rm_vpc_data})
        self.vpc.update(module_data)

    def v_internet_gateway(self):
        module_data, rm_ig_data = self._global_validator(self.internet_gateway, internet_gateway_validator)
        state.data.update({'ig': rm_ig_data})
        self.internet_gateway.update(module_data)

    def resource_validator(self, data: list, validator_func, resource_key):
        resource_data = {}
        for index, rs_data in enumerate(data):
            module_data, _rm_data = self._global_validator(rs_data, validator_func)
            resource_data.update(_rm_data)
            data[index].update(module_data)
        state.data.update({resource_key: resource_data})
