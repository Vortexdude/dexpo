from dexpo.src.lib.utils import Util
from dexpo.src.controller.validator import ValidateHandler
from dexpo.src.controller.deployer import DeployHandler
from dexpo.settings import Files


class Controller(object):
    def __init__(self, data=None):
        self.data = data.model_dump() if data else {}

    @staticmethod
    def store_state(file=Files.STATE_FILE_PATH, data=None):
        Util.save_to_file(file, {"vpcs": data})

    def validate(self):
        _vpsStates = []
        for vpc_data in self.data['vpcs']:
            ValidateHandler(vpc_data)
            _vpsStates.append(vpc_data)
        self.store_state(data=_vpsStates)

    def apply(self):
        data = Util.load_json(Files.STATE_FILE_PATH)
        for vpc_data in data['vpcs']:
            dh = DeployHandler(data=vpc_data)
            dh.launch()

    def destroy(self):
        print('destroying...')
