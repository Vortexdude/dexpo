import os.path
from dexpo.src.lib.utils import Util
from dexpo.settings import Files
from dexpo.settings import pluginManager

SEQUENCE = ['vpc', 'internet_gateway', 'route_tables', 'subnets', 'security_groups']


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}
        if not Util.file_existence(Files.STATE_FILE_PATH):
            Util.save_to_file(Files.STATE_FILE_PATH, self.data)

    @staticmethod
    def store_state(file=Files.STATE_FILE_PATH, data=None):
        Util.save_to_file(file, {"vpcs": data})

    def validate(self):
        action = 'validate'
        for global_vpc in self.data['vpcs']:
            for module in SEQUENCE:
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

    def apply(self):
        action = 'create'
        for global_vpc in self.data['vpcs']:
            for module in SEQUENCE:
                if not isinstance(global_vpc[module], list):  # loop through non list items
                    pluginManager.call_plugin(
                        plugin_name=module,
                        action=action,
                        data=global_vpc[module]
                    )
                else:
                    for index, resource in enumerate(global_vpc[module]):
                        pluginManager.call_plugin(
                            plugin_name=module,
                            action=action,
                            data=global_vpc[module][index],
                            index=index
                        )

    # def apply(self):
    #     data = Util.load_json(Files.STATE_FILE_PATH)
    #     for vpc_data in data['vpcs']:
    #         dh = DeployHandler(data=vpc_data)
    #         dh.launch()
    #
    # def destroy(self):
    #     print('destroying...')
