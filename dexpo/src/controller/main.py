from dexpo.src.lib.utils import Util
from dexpo.settings import Files
from dexpo.settings import pluginManager, state_file_storage

if state_file_storage == 's3':
    from dexpo.settings import Backend
    from dexpo.src.lib.modules import upload_to_s3, file_exists, download_state

LAUNCH_SEQUENCE = {
    'vpcs': ['vpc', 'internet_gateway', 'route_tables', 'subnets', 'security_groups'],
    'ec2': ['ec2']
}
DELETE_SEQUENCE = {
    'vpcs': ['internet_gateway', 'subnets', 'route_tables', 'security_groups', 'vpc'],
    'ec2': ['ec2']
}


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}
        if not Util.file_existence(Files.STATE_FILE_PATH):
            if state_file_storage == 's3':
                if file_exists(Backend.BUCKET_NAME, Backend.OBJECT_NAME):
                    download_state(Backend.BUCKET_NAME, Backend.OBJECT_NAME, Backend.FILE_NAME)
                else:
                    Util.save_to_file(Files.STATE_FILE_PATH, self.data)
            else:
                Util.save_to_file(Files.STATE_FILE_PATH, self.data)

    def _process_vpcs(self, action):
        for global_vpc in self.data['vpcs']:
            for module in LAUNCH_SEQUENCE['vpcs']:
                if not isinstance(global_vpc[module], list):  # loop through non list items
                    pluginManager.call_plugin(
                        plugin_name=module,
                        action=action,
                        data=global_vpc[module]
                    )
                else:  # loop through list items
                    for index, resource in enumerate(global_vpc[module]):
                        pluginManager.call_plugin(
                            plugin_name=module,
                            action=action,
                            data=global_vpc[module][index],
                            index=index
                        )

    def validate(self):
        action = 'validate'
        self._process_vpcs(action)
        for ec2 in self.data['ec2']:
            pluginManager.call_plugin(plugin_name='ec2', action=action, data=ec2)
        for s3 in self.data['s3']:
            pluginManager.call_plugin(plugin_name='s3', action=action, data=s3)

    def apply(self):
        action = 'create'
        self._process_vpcs(action)
        for ec2 in self.data['ec2']:
            pluginManager.call_plugin(plugin_name='ec2', action=action, data=ec2)
        for s3 in self.data['s3']:
            pluginManager.call_plugin(plugin_name='s3', action=action, data=s3)

        if state_file_storage == 's3':
            upload_to_s3(Backend.BUCKET_NAME, Backend.FILE_NAME, Backend.OBJECT_NAME)

    def destroy(self):
        action = 'delete'
        for ec2 in self.data['ec2']:
            pluginManager.call_plugin(plugin_name='ec2', action=action, data=ec2)
        for s3 in self.data['s3']:
            pluginManager.call_plugin(plugin_name='s3', action=action, data=s3)

        sequence = DELETE_SEQUENCE['vpcs']
        data = Util.load_json(Files.STATE_FILE_PATH)
        for global_vpc in data.get('vpcs', []):
            for module in sequence:
                if not isinstance(global_vpc[module], list):  # loop through non list items
                    pluginManager.call_plugin(plugin_name=module, action=action, data=global_vpc[module])
                else:
                    for index, resource in enumerate(global_vpc[module]):
                        pluginManager.call_plugin(
                            plugin_name=module,
                            action=action,
                            data=global_vpc[module][index],
                            index=index
                        )

        if state_file_storage == 's3':
            upload_to_s3(Backend.BUCKET_NAME, Backend.FILE_NAME, Backend.OBJECT_NAME)
