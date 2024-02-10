import logging
import json
import os
import pathlib
import argparse
from enum import Enum
from devops.resources.const import DISPLAY_TEXT, _SUBNET, _ROUTE_TABLE, _SECURITY_GROUP, _INTERNET_GATEWAY, _VPC, _EC2


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

    custom_format = "%(logger_namespace)s %(levelname)s %(filename)10s:%(lineno)s -%(funcName)10s() %(message)s"

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
            raise Exception("Error: Please specify the log level.")

        log_levels = {
            'critical': logging.CRITICAL,
            'error': logging.ERROR,
            "warning": logging.WARNING,
            "warn": logging.WARN,
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


class Utils:

    @staticmethod
    def read_json(file: str) -> dict:
        """
        Read the json file and return the json data 
        required the file name only it will resolve the path automatically

        """
        current_path = pathlib.Path().resolve()
        file = f"{current_path}/devops/{file}"
        with open(file) as JSON:
            json_dict = json.load(JSON)
        return json_dict

    @staticmethod
    def convert_json(data: dict):
        """Convert dict to json"""
        r = json.dumps(data)
        return r

    @staticmethod
    def write_to_file(filename: str, data: dict):
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)


class Parser(argparse.ArgumentParser):
    def __init__(self):
        description = """
        Dexpo repository is used to create cloud infrastructure in AWS
        
        """
        epilog = """Print At the END"""
        super().__init__(
            description=description,
            epilog=epilog
        )
        self.add_all_arguments()

    def add_all_arguments(self):
        self.add_argument(
            'action',
            nargs="?",
            choices=["apply", "destroy"],
            help='Do some homework'
        )
        if not self.parse_args().action:
            return self.print_help()

    @property
    def args(self):
        return super().parse_args()


class DexColors:
    class Color(Enum):
        DEBUG = '\033[94m'
        CYAN = '\033[96m'
        SUCCESS = '\033[92m'
        WARNING = '\033[93m'
        ERROR = '\033[91m'
        INFO = '\033[4m'
        RESET = '\033[0m'

    def __init__(self):
        self.header = '\033[95m'
        self.bold = '\033[1m'

    def dprint(self, color: Color, text: str) -> str:
        """
        Apply color to the given text.

        Parameters:
        - color (Color): The color to apply.
        - text (str): The text to color.

        Returns:
        str: The colored text.
        """

        return f"{color.value}{text}{self.Color.RESET.value}"


def dex_wrapper(level: str, item: dict, _tmp_text):
    dex_colors: DexColors = DexColors()
    resource_name = list(item.keys())[0]
    resource_id = item[resource_name][1]
    resource_type: str = item[resource_name][2].lower()

    level_mapping = {
        'debug': dex_colors.Color.DEBUG,
        'info': dex_colors.Color.SUCCESS,
        'warning': dex_colors.Color.WARNING,
        'danger': dex_colors.Color.ERROR
    }

    resource_mapping = {
        "subnet": (_SUBNET, resource_name, resource_id),
        "security_group": (_SECURITY_GROUP, resource_name, resource_id)
    }
    if _SUBNET not in _tmp_text:  # for removing extra banner
        _tmp_text += resource_mapping[resource_type][0]
    _tmp_text += DISPLAY_TEXT.format(
        name=resource_mapping[resource_type][1],
        id=resource_mapping[resource_type][2] if resource_mapping[resource_type][2] else "Known after apply",
        text=f"Adding new {resource_type.capitalize()}"
    )

    return dex_colors.dprint(level_mapping[level], _tmp_text)


class Config:
    @staticmethod
    def load_json(file: str) -> dict:
        """
        Read the json file and return the json data
        required the file name only it will resolve the path automatically

        """
        with open(file) as JSON:
            json_dict = json.load(JSON)
        return json_dict
