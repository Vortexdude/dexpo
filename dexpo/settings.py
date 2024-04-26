from dexpo.src.lib.parser import DexpoArgParser
from dexpo.src.lib.utils import get_conf
from dexpo.src.lib.utils import validate_aws_credentials, DexLogger, Util
import os
from dexpo.banner import banner
project_name = 'dexpo'

DEBUG = True

if DEBUG:
    log_level = 'debug'
else:
    log_level = 'info'

project_home_dir_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
user_home_dir = os.path.expanduser('~')
config_dir_path = os.path.join(project_home_dir_path, 'config', "config.json")
state_file_path = os.path.join(project_home_dir_path, 'state.json')
temp_state_file_path = os.path.join(project_home_dir_path, 'temp_state.json')


class Files:
    CONFIG_FILE_PATH = config_dir_path
    STATE_FILE_PATH = state_file_path
    TEMP_STATE_FILE_PATH = temp_state_file_path


print(banner)

loginit = DexLogger(log_level, project_name)
logger = loginit.get_logger()

logger.debug("Logging Initialize ... .. .")

project_aws_credentials_path = os.path.join(project_home_dir_path, '.aws', 'credentials')
user_aws_credentials_path = os.path.join(user_home_dir, '.aws', 'credentials')


def initializer():
    """Add new function to validate something before run the program"""
    try:
        validate_aws_credentials(project_aws_credentials_path, user_aws_credentials_path)
        logger.debug("Credentials found in the desired path")
    except FileNotFoundError as e:
        logger.error("No credentials found in the desired location")


args = DexpoArgParser()

CONF = get_conf(config_dir_path)

logger.debug(
    f"Config loaded source from: {config_dir_path} ."
)
from dexpo.src.lib.utils import PLUGIN_DIRECTORY
logger.debug(
    "\n\n \
    #-- start: project settings --# \n \
    project_name: {} \n \
    project_home_path: {} \n \
    config_file_path: {} \n \
    plugin_directory: {} \n \
    -- end: project settings -- \n \n \
        ".format(
        project_name, project_home_dir_path, config_dir_path, PLUGIN_DIRECTORY
    ),
)
