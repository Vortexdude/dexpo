import os
import json
import sys
import importlib
import logging
from errno import EACCES, EPERM
from dexpo.src.lib.models import ConfigModel

project_name = 'dexpo'
HOME_DIR = os.path.expanduser('~')
USER_AWS_FILE_PATH = os.path.join(HOME_DIR, '.aws', 'credentials')
CURRENT_WORKING_DIR = os.getcwd()
STATE_FILE_PATH = os.path.join(CURRENT_WORKING_DIR, 'state.json')
TEMP_STATE_FILE_PATH = os.path.join(CURRENT_WORKING_DIR, 'temp_state.json')
PLUGIN_DIRECTORY = os.path.join(CURRENT_WORKING_DIR, project_name, 'src', 'resources', 'vpc')
env_vars: dict = {'DEBUG': True}


class Util:
    # https://stackoverflow.com/questions/20199126/reading-json-from-a-file
    @staticmethod
    def is_file(file):
        """check the file exits or not"""
        return os.path.isfile(file)

    @staticmethod
    def file_existence(file_path: str):
        return os.path.exists(file_path)

    @staticmethod
    def load_json(file):
        if not Util.is_file(file):
            print("File does not exist or is not readable.")
            sys.exit(127)
        try:
            with open(file) as f:
                data = json.load(f)
            return data
        except json.JSONDecodeError as e:
            print("Invalid JSON syntax:", e, file)
            sys.exit(1)
        except IOError as err:
            if err.errno in (EACCES, EPERM):
                print("Permission denied: You don't have the read permission.")
                sys.exit()
            else:
                raise err

    @staticmethod
    def save_to_file(filename: str, data: dict):
        """
        Write dictionary data to a JSON file.

        Parameters:
        - filename: Name of the file to write the JSON data to.
        - data: Dictionary containing the data to be written to the file.
        """
        with open(filename, "w") as json_file:
            json.dump(data, json_file, indent=4)

    @staticmethod
    def remove_file(filename: str):
        if os.path.exists(filename):
            os.remove(filename)
        else:
            print(f"The file {filename} does not exist")


class DexFormatter(logging.Formatter):
    GREEN = "\x1b[32m"
    BLUE = "\033[0;34m"
    PURPLE = "\033[0;35m"
    CYAN = "\033[0;36m"
    GRAY = "\x1b[38;20m"
    LIGHT_GRAY = "\033[0;37m"
    YELLOW = "\x1b[33;20m"
    RED = "\x1b[31;20m"
    BOLD_RED = "\x1b[31;1m"
    WHITE = "\x1b[0m"
    RESET = "\x1b[0m"

    custom_format = "[%(asctime)s][%(levelname)s] - %(message)s - %(filename)8s:%(lineno)s -%(funcName)10s()"

    FORMAT = {
        logging.DEBUG: GRAY + custom_format + RESET,
        logging.INFO: CYAN + custom_format + RESET,
        logging.WARNING: YELLOW + custom_format + RESET,
        logging.ERROR: RED + custom_format + RESET,
        logging.CRITICAL: BOLD_RED + custom_format + RESET
    }

    def format(self, record):
        log_fmt = self.FORMAT.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)


class DexLogger:
    def __init__(self, log_level, logger_namespace):
        if log_level is None:
            raise Exception("Please Specify the loglevel")

        log_levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            'warning': logging.WARN,
            'warn': logging.WARNING,
            'info': logging.INFO,
            'debug': logging.DEBUG
        }
        logger = logging.getLogger(__name__)

        logger.setLevel(log_levels[log_level])
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(DexFormatter())
        logger.addHandler(console_handler)
        self.logger = logging.LoggerAdapter(
            logger,
            {"logger_namespace": logger_namespace}
        )
        self.log_level = self.logger.logger.level

    def get_logger(self):
        return self.logger


def set_env_variables(*args, **kwargs):
    """
    Set environment variables based on key-value pairs provided in kwargs.

    Parameters:
        *args: Positional arguments (not used in this function).
        **kwargs: Key-value pairs where the key is the environment variable name
                  and the value is the environment variable value.

    Example:
        >>> set_env_variables(DB_HOST='localhost', DB_PORT='5432', DEBUG_MODE='True')
    """
    for key, value in kwargs.items():
        set_env(key, value)


def get_conf(file) -> ConfigModel:
    """
    Load configuration data from a JSON file and return a ConfigModel object.

    Parameters:
    - file (str): The path to the JSON file containing configuration data.

    Returns:
    - ConfigModel: An instance of ConfigModel containing the loaded configuration data.

    Raises:
    - FileNotFoundError: If the specified file does not exist.
    - JSONDecodeError: If the JSON data in the file is invalid.

    Example:
    >>> config = get_conf("config.json")
    >>> print(config)
    ConfigModel(attr1='value1', attr2='value2', ...)

    This function loads configuration data from a JSON file and initializes a ConfigModel
    object with the loaded data. The ConfigModel class should have attributes corresponding
    to the keys in the JSON object. It's expected that the JSON file contains a valid
    configuration structure that can be deserialized into a dictionary.

    Note:
    - The ConfigModel class should be defined with attributes corresponding to the keys
      in the JSON object. This function relies on the constructor of ConfigModel accepting
      keyword arguments.

    - This function relies on the 'load_json' function, which should be defined elsewhere
      in the codebase and be responsible for loading JSON data from a file.

    Example Usage:
    We can load this configuration using the get_conf function:
    >>> config = get_conf("config.json")
    >>> print(config)
    ConfigModel(attr1='value1', attr2='value2', ...)
    """
    config_data = Util.load_json(file)
    return ConfigModel(**config_data)


def print_all_env():
    for name, value in os.environ.items():
        print("{0}: {1}".format(name, value))


def set_env(var, value):
    os.environ[var] = str(value)


def get_env(var):
    return os.environ.get(var)


def validate_aws_credentials(aws_credentials_paths):
    for file in aws_credentials_paths:
        if Util.file_existence(file):
            return False

    if 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
        return True

    else:
        raise FileNotFoundError("AWS credentials file not found in user's home directory or project's home directory.")


def check_credentials(*args, **kwargs):
    try:
        validate_aws_credentials(*args, **kwargs)
    except FileNotFoundError as e:
        print("Error ", e)


def creds_validator():
    if not check_credentials():
        message = """
        WARNING: AWS credentials not found!

        Please make sure to set your AWS credentials either by:

        1. Creating a credentials file (typically located at ~/.aws/credentials) with the following format:

            [default]
            aws_access_key_id = YOUR_ACCESS_KEY_ID
            aws_secret_access_key = YOUR_SECRET_ACCESS_KEY

        For more information on creating a credentials file, refer to the AWS documentation:
        https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-files.html

        OR

        2. Setting the following environment variables:

            - AWS_ACCESS_KEY_ID: Your AWS access key ID
            - AWS_SECRET_ACCESS_KEY: Your AWS secret access key

        For more information on setting environment variables, refer to the AWS documentation:
        https://docs.aws.amazon.com/cli/latest/userguide/cli-configure-envvars.html

        Not setting AWS credentials can lead to authentication errors when interacting with AWS services."""
        print(message)
        sys.exit(101)


def get_class_variable(class_name, default=False) -> list | dict:
    """For Getting the class variables in the LIST and DICT form it should be in the capitol letters"""

    if default:
        attr = {}
        data = vars(class_name)
        for k, v in data.items():
            if not k.startswith('__'):
                if 'function' not in str(v):
                    attr.update({k: v})
        return attr
    else:
        attr = []
        for _attr in dir(class_name):
            if not str(_attr).startswith("__") and str(_attr).isupper():
                attr.append(_attr)
        return attr


PROJECT_HOME_PATH = os.getcwd()


class Dexpo:
    def __init__(self):
        self.resources = []

    def load_resource(self, resource_directory):
        """
        Load resource from the specified directory.

        Parameters:
            resource_directory (str): The directory containing resource modules.
        """
        for filename in os.listdir(resource_directory):
            if filename.endswith('.py') and filename != '__init__.py':
                module_name = os.path.splitext(filename)[0]
                module = importlib.import_module(f"dexpo.src.{module_name}")
                for name in dir(module):
                    obj = getattr(module, name)
                    if hasattr(obj, '__bases__') and Dexpo in obj.__bases__:
                        self.resources.append(obj())

    def run_class_method(self, method_name, *args, **kwargs):
        """
        Run a method of all loaded resource.

        Parameters:
            method_name (str): The name of the method to run.
            *args: Positional arguments to pass to the method.
            **kwargs: Keyword arguments to pass to the method.
        """
        for resource in self.resources:
            if hasattr(resource, method_name):
                method = getattr(resource, method_name)
                method(*args, **kwargs)


class PluginManager:
    def __init__(self, plugin_path, project_home):
        self.plugins = []
        self.plugin_path = plugin_path
        self._set_all_paths(project_home)
        self._find_all_plugins()

    def _set_all_paths(self, home_dir):
        self.plugin_relative_path = self.plugin_path.replace(home_dir + '/', '')
        self.plugin_path_import_style = str(self.plugin_relative_path.replace('/', '.'))

    def _find_all_plugins(self):
        for filename in os.listdir(self.plugin_path):
            if filename.endswith('.py') and filename != "__init__.py":
                self.plugins.append(os.path.splitext(filename)[0])

    def load_plugin(self, name):
        if not name:
            raise Exception(f"Given plugin {name} not found in the directory")

        import importlib
        mod = importlib.import_module(self.plugin_path_import_style + name)
        return mod

    def call_plugin(self, plugin_name, *args, **kwargs):
        if plugin_name and plugin_name in self.plugins:
            plugin = self.from_spec(plugin_name)  # plugin = self.load_plugin(plugin_name)
            # print(f"plugin imported {plugin.__name__}")
            # print(f"plugin documentation {plugin.__doc__}")
            # print("Directory list of the imported module: ", dir(plugin))
            return plugin.run_module(*args, **kwargs)

    def from_spec(self, name: str):
        if name in self.plugins:
            import importlib.util
            module_spec = importlib.util.find_spec(self.plugin_path_import_style + name)
            module = importlib.util.module_from_spec(module_spec)
            module_spec.loader.exec_module(module)
            return module


class VpcState(object):
    def __init__(self, d: dict = None):
        if d is not None:
            for key, value in d.items():
                setattr(self, key, value)
