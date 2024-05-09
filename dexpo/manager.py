from dexpo.settings import logger, Files
from dexpo.src.lib.utils import Util


class DexpoModule(object):
    def __init__(self, base_arg, extra_args=None, *args, module_type=None, **kwargs):
        self.base_args = base_arg
        self.extra_args = extra_args
        self.state_file_path = Files.STATE_FILE_PATH
        self.temp_state_file_path = Files.TEMP_STATE_FILE_PATH
        self.module_type = module_type if module_type else None
        # print("you can validate in the constructor of the DexpoModule \nBefore calling the method")

    def get_resource_values(self, vpc_resource, resource_name, request):
        _current_state = self.get_state()
        for vpc_entry in _current_state.get('vpcs', []):
            if self.extra_args.get('resource_type') == 'list':
                index = self.extra_args['index']
                if vpc_entry.get(vpc_resource)[index].get('name') == resource_name:
                    if request == 'VpcId':
                        return vpc_entry['vpc']['VpcId']
                    elif request == 'InternetGatewayId':
                        return vpc_entry['internet_gateway']['InternetGatewayId']
                    elif request == 'RouteTableId':
                        rt_name = vpc_entry.get(vpc_resource)[index].get('route_table')  # from subnet get route table
                        for rt in vpc_entry.get('route_tables'):  # from route tables fetch the above one.
                            if rt['name'] == rt_name:
                                return rt['RouteTableId']

                        return vpc_entry['internet_gateway']['InternetGatewayId']
                    else:
                        return
            else:
                if vpc_entry.get(vpc_resource).get('name') == resource_name:
                    if request == 'VpcId':
                        return vpc_entry['vpc']['VpcId']
                    elif request == 'InternetGatewayId':
                        return vpc_entry['internet_gateway']['InternetGatewayId']
                    else:
                        return

    def validate_resource(self, identity, response, *args, **kwargs):
        """It will check the identity key in the response and key in the state file"""

        if identity not in response:
            return False

        current_state = self.get_state()
        for vpc_entry in current_state.get('vpcs', []):
            if self.extra_args['resource_type'] == 'list':  # check for list type.
                index = int(self.extra_args['index'])
                if vpc_entry.get(self.module_type)[index].get(identity) == response[identity]:
                    return True
            else:
                if vpc_entry.get(self.module_type, {}).get(identity) == response[identity]:
                    return True

        return False

    def save_state(self, data):
        temp_data = self.get_state()
        if not data and 'vpcs' not in temp_data:  # return if not data
            return

        for global_vpc in temp_data['vpcs']:
            if self.module_type not in global_vpc:  # return if module not found
                return

            if self.extra_args['resource_type'] == 'list':  # check for list type.
                index = int(self.extra_args['index'])
                global_vpc[self.module_type][index].update(data)
            else:
                global_vpc[self.module_type].update(data)

            Util.save_to_file(self.state_file_path, temp_data)  # save to file
            self.logger.debug(f"Data Stored in state {self.state_file_path}.")

    def update_state(self, state, data):
        pass

    def get_state(self) -> dict | None:
        return Util.load_json(self.state_file_path)

    @property
    def logger(self) -> logger:
        return logger

    def cleanup(self):
        Util.remove_file(self.temp_state_file_path)


class SkipExecutionException(Exception):
    pass
