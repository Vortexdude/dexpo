import os.path
from dexpo.src.lib.utils import Util
from dexpo.settings import Files
from dexpo.settings import pluginManager
from dexpo.src.lib.utils import VpcState

state = VpcState()


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
            modules = list(global_vpc.keys())  # every key in the config refers to a plugin file name
            for module in modules:
                if not isinstance(global_vpc[module], list):  # loop through non list items
                    pluginManager.call_plugin(
                        plugin_name=module,
                        action=action,
                        data=global_vpc[module]
                    )

                else:  # loop through list items
                    pass

    def apply(self):
        action = 'create'
        for global_vpc in self.data['vpcs']:
            modules = list(global_vpc.keys())  # every key in the config refers to a plugin file name
            for module in modules:
                if not isinstance(global_vpc[module], list):  # loop through non list items
                    pluginManager.call_plugin(
                        plugin_name=module,
                        action=action,
                        data=global_vpc[module]
                    )
    #
    # def apply(self):
    #     data = Util.load_json(Files.STATE_FILE_PATH)
    #     for vpc_data in data['vpcs']:
    #         dh = DeployHandler(data=vpc_data)
    #         dh.launch()
    #
    # def destroy(self):
    #     print('destroying...')
