import os
import pathlib
import devops.models.config
from devops.lib.utils import DexLogger
from devops.lib.utils import Config

# get the current path
# https://stackoverflow.com/questions/3430372/how-do-i-get-the-full-path-of-the-current-files-directory

# parser
# https://github.com/kblomqvist/yasha/blob/master/yasha/yasha.py

project_home_path = pathlib.Path(__file__).parent.resolve()
project_name = os.path.basename(project_home_path)
state_file_path = os.path.join(project_home_path, 'devops', 'state')
config_file_path = os.path.join(project_home_path, 'devops', 'env')

loginit = DexLogger("debug", project_name)
logger = loginit.get_logger()

logger.debug("Logging Initialize ... .. .")

config = Config.load_json(file=os.path.join(config_file_path, 'config.json'))


def store_state(data: dict):
    _state_file_path = os.path.join(state_file_path, 'state.json')
    if Config.file_existence(_state_file_path):
        Config.write_to_file(filename=os.path.join(state_file_path, 'state.json'), data=data)
        logger.info(f"Generated the state file {state_file_path}")

    else:
        logger.warning(f"State file not present {state_file_path}")

try:
    conf = devops.models.config.RootModel(**config).model_dump()
except:
    logger.error(f"Model validation failed")
    raise Exception("Correct the Config file syntax or validate with model")

vpcs = conf['vpcs']
ec2s = conf['ec2']

logger.debug(
    f"Config loaded source from: {config_file_path} ."
)

logger.debug(
    "\n\n \
#-- start: project settings --# \n \
project_name: {} \n \
project_home_path: {} \n \
config_file_path: {} \n \
-- end: project settings -- \n \
        ".format(
        project_name, project_home_path, config_file_path
    ),
)
