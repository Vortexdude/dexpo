from dexpo.settings import logger
from dexpo.src.lib.state_management import state
from dexpo.settings import dexpo


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
        try:
            self.validate_vpc()
            self.validate_internet_gateway()
            self.validate_route_tables()
            self.validate_subnets()
            self.validate_security_groups()
        except Exception as e:
            logger.error(f"{e}")

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

    def validate_vpc(self):
        vpc_module_data = dexpo.run_plugin_method('validate_vpc', self.vpc)
        if not vpc_module_data:
            return
        _id, _resource = self.extractor(vpc_module_data)
        _vpc_formatted_data = state.formatter(name=self.vpc['name'], _id=_id, resource=_resource)
        del vpc_module_data['resource']
        state.data.update({'vpc': _vpc_formatted_data})
        self.vpc.update(vpc_module_data)

    def validate_internet_gateway(self):
        ig_module_data = dexpo.run_plugin_method('validate_ig', self.internet_gateway)
        if not ig_module_data:
            return
        _id, _resource = self.extractor(ig_module_data)
        _ig_formatted_data = state.formatter(name=self.internet_gateway['name'], _id=_id, resource=_resource)
        del ig_module_data['resource']
        state.data.update({'ig': _ig_formatted_data})
        self.internet_gateway.update(ig_module_data)

    def validate_route_tables(self):
        self._custom_validator(data=self.route_tables, resource_name='rt', runner_method='validate_rt')

    def validate_subnets(self):
        self._custom_validator(data=self.subnets, resource_name='sb', runner_method='validate_sb')

    def validate_security_groups(self):
        self._custom_validator(data=self.security_groups, resource_name='sg', runner_method='validate_sg')

    def _custom_validator(self, data: list, resource_name: str, runner_method: str):
        _resource_data = {}
        for index, resource_data in enumerate(data):
            module_data = dexpo.run_plugin_method(runner_method, resource_data)
            if not module_data:
                continue

            _id, _resource = self.extractor(module_data)
            del module_data['resource']
            data[index].update(module_data)
            _module_formatted_data = state.formatter(name=resource_data['name'], _id=_id, resource=_resource)
            _resource_data.update(_module_formatted_data)
        state.data.update({resource_name: _resource_data})
