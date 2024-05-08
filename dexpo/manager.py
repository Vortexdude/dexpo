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

    def save_state(self, data):
        temp_data = self.get_state()
        if data:
            if 'vpcs' not in temp_data:
                return
            for global_vpc in temp_data['vpcs']:
                if self.module_type not in global_vpc:
                    return
                global_vpc[self.module_type].update(data)
                Util.save_to_file(self.state_file_path, temp_data)
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
