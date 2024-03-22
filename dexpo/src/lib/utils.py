import os
import json
import sys
from errno import EACCES, EPERM


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

# Default path can be changed in program
CONFIG_FILE_PATH = os.path.join(PROJECT_HOME_PATH, 'config')


def is_file(file):
    """check the file exits or not"""
    return os.path.isfile(file)


# https://stackoverflow.com/questions/20199126/reading-json-from-a-file
def load_json(file):
    if not is_file(file):
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
