from dexpo.src.lib.parser import DexpoArgParser
from dexpo.src.lib.utils import load_json
from dexpo.src.lib.models import ConfigModel
from dexpo.src.lib.utils import creds_validator, CONFIG_FILE_PATH


def initializer():
    """Add new function to validate something before rn the program"""

    creds_validator()


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
    config_data = load_json(file)
    return ConfigModel(**config_data)


args = DexpoArgParser()

CONF = get_conf(CONFIG_FILE_PATH)
