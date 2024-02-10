import os
import pathlib

import devops.models.config
from devops.lib.utils import DexLogger
from devops.lib.utils import Config

project_home_path = pathlib.Path(__file__).parent.resolve()
project_name = os.path.basename(project_home_path)
state_file_path = os.path.join(project_home_path, 'state')
config_file_path = os.path.join(project_home_path, 'env')

loginit = DexLogger("debug", project_name)
logger = loginit.get_logger()

logger.info("Logging Initialize ... .. .")

config = Config.load_json(file=os.path.join(config_file_path, 'config.json'))

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
