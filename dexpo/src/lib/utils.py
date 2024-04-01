import os
import json
import sys
from errno import EACCES, EPERM
from abc import ABCMeta, abstractmethod

HOME_DIR = os.path.expanduser('~')
USER_AWS_FILE_PATH = os.path.join(HOME_DIR, '.aws', 'credentials')
CURRENT_WORKING_DIR = os.getcwd()
CONFIG_FILE_PATH = os.path.join(CURRENT_WORKING_DIR, 'config', 'config.json')


def get_env(var):
    return os.environ.get(var)


def check_credentials():
    if os.path.exists(USER_AWS_FILE_PATH):
        return True

    if 'AWS_ACCESS_KEY_ID' in os.environ and 'AWS_SECRET_ACCESS_KEY' in os.environ:
        return True

    return False


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


class BaseAbstractmethod(metaclass=ABCMeta):

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def to_dict(self, prop: dict):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def delete(self):
        pass
