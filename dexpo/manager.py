from dexpo.settings import logger, Files
from dexpo.src.lib.utils import Util


class DexpoModule(object):
    """Helper Main Class for creating Plugins"""
    def __init__(self, base_arg, extra_args=None, *args, module_type=None, **kwargs):
        self.base_args = base_arg
        self.extra_args = extra_args
        self.state_file_path = Files.STATE_FILE_PATH
        self.temp_state_file_path = Files.TEMP_STATE_FILE_PATH
        self.module_type = module_type if module_type else None

    def get_resource_values(self, vpc_resource, resource_name, request):
        """
        Get the specified value of a resource within a VPC.

        Parameters:
            vpc_resource (str): The type of VPC resource (e.g., 'subnet', 'security_group').
            resource_name (str): The name of the resource whose value needs to be retrieved.
            request (str): The specific value to retrieve (e.g., 'VpcId', 'InternetGatewayId', 'RouteTableId').

        Returns:
            str or None: The requested value of the resource, or None if not found.

        Raises:
            None

        Note:
            - This method searches for the specified resource within the VPC and retrieves its associated value.
            - For resources stored in a list (e.g., multiple subnets), the index of the resource must be provided.
            - If the requested value is not found, None is returned.
            """

        _current_state = self.get_state()
        if resource_name == 'ec2':
            vpc_name = self.base_args.vpc
            for vpc_entry in _current_state.get('vpcs', []):
                if 'subnet' in request.lower():
                    for sb in vpc_entry['subnets']:
                        if sb.get('name') == self.base_args.subnet:
                            return sb.get('SubnetId')
                if 'securitygroup' in request.lower():
                    securitygroupids = []
                    for sg in self.base_args.security_groups:
                        for _sg in vpc_entry['security_groups']:
                            if _sg.get('name') == sg:
                                securitygroupids.append(_sg['GroupId'])
                    return securitygroupids

                if vpc_entry.get(vpc_resource).get('name') == vpc_name:
                    return vpc_entry.get(vpc_resource).get(request, '')

        for vpc_entry in _current_state.get('vpcs', []):
            if self.extra_args.get('resource_type') == 'list':
                index = self.extra_args['index']
                if vpc_entry.get(vpc_resource)[index].get('name') == resource_name:
                    if request == 'VpcId':
                        return vpc_entry['vpc'][request]
                    elif request == 'InternetGatewayId':
                        return vpc_entry['internet_gateway'][request]
                    elif request == 'RouteTableId':
                        rt_name = vpc_entry.get(vpc_resource)[index].get('route_table')  # from subnet get route table
                        for rt in vpc_entry.get('route_tables'):  # from route tables fetch the above one.
                            if rt['name'] == rt_name:
                                return rt[request]

                        return vpc_entry['internet_gateway']['InternetGatewayId']
                    else:
                        return
            else:
                if vpc_entry.get(vpc_resource).get('name') == resource_name:

                    if request == 'VpcId':
                        if request not in vpc_entry['vpc']:
                            return
                        return vpc_entry['vpc'][request]

                    elif request == 'InternetGatewayId':
                        if request not in vpc_entry['internet_gateway']:
                            return

                        return vpc_entry['internet_gateway'][request]
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

        if self.module_type == 'ec2':
            for index, ec2 in enumerate(temp_data.get('ec2', [])):
                if ec2.get('name') == self.base_args.name:
                    if self.extra_args['action'] == 'delete':
                        temp_data['ec2'][index] = data
                    else:
                        temp_data['ec2'][index].update(data)
                    Util.save_to_file(self.state_file_path, temp_data)  # save to file
                    self.logger.debug(f"Data Stored in state {self.state_file_path}.")
        else:
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

    def update_state(self, data):
        _vpc_state = self.get_state()
        if 'ec2' in self.module_type:
            _state = _vpc_state.copy()
            for index, global_vpc in enumerate(_state.get('ec2', [])):
                _state['ec2'][index] = data
            Util.save_to_file(Files.STATE_FILE_PATH, _state)
            logger.debug(f"file saved for {self.module_type}")
        else:
            for global_vpc in _vpc_state.get('vpcs', []):
                if self.module_type in global_vpc:
                    if self.extra_args['resource_type'] == 'list':
                        index = self.extra_args['index']
                        global_vpc[self.module_type][index] = data
                    else:
                        global_vpc[self.module_type] = data
            Util.save_to_file(self.state_file_path, _vpc_state)
            logger.debug(f"file saved for {self.module_type}")

    def get_state(self) -> dict | None:
        return Util.load_json(self.state_file_path)

    @property
    def logger(self) -> logger:
        return logger

    def cleanup(self):
        Util.remove_file(self.temp_state_file_path)


class SkipExecutionException(Exception):
    pass