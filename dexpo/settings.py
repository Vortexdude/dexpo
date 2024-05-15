from dexpo.src.lib.parser import DexpoArgParser
from dexpo.src.lib.utils import DexLogger, PluginManager, validate_aws_credentials, get_conf
import os
from dexpo.banner import banner
project_name = 'dexpo'

DEBUG = True

if DEBUG:
    log_level = 'debug'
else:
    log_level = 'info'

project_base_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
project_home_dir_path = os.path.join(project_base_path, project_name)
config_dir_path = os.path.join(project_home_dir_path, 'config', "config.json")
state_file_path = os.path.join(project_home_dir_path, 'state.json')
temp_state_file_path = os.path.join(project_home_dir_path, 'temp_state.json')
default_plugin_path = os.path.join(project_home_dir_path, 'src/plugins/')


pluginManager = PluginManager(plugin_path=default_plugin_path, project_home=project_base_path)


class Files:
    CONFIG_FILE_PATH = config_dir_path
    STATE_FILE_PATH = state_file_path
    TEMP_STATE_FILE_PATH = temp_state_file_path


print(banner)

loginit = DexLogger(log_level, project_name)
logger = loginit.get_logger()

logger.debug("Logging Initialize ... .. .")

aws_credentials_paths = [
    os.path.expanduser('~/.aws/credentials'),
    os.path.join(project_home_dir_path, '.aws', 'credentials')
]


def initializer():
    """Add new function to validate something before run the program"""
    try:
        validate_aws_credentials(aws_credentials_paths)
        logger.debug("Credentials found in the desired path")
    except FileNotFoundError:
        logger.error("No credentials found in the desired location")
        import sys
        sys.exit(0)


args = DexpoArgParser()

CONF = get_conf(config_dir_path)

logger.debug(
    f"Config loaded source from: {config_dir_path} ."
)

logger.debug(
    "\n\n \
    #-- start: project settings --# \n \
    project_name: {} \n \
    project_home_path: {} \n \
    config_file_path: {} \n \
    -- end: project settings -- \n \n \
        ".format(
        project_name, project_home_dir_path, config_dir_path
    ),
)
