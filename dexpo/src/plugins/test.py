import os
import sys
from dexpo.settings import logger


class DexpoModule(object):
    def __init__(self, base_arg, extra_args=None):
        self.base_Args = base_arg
        self.extra_args = extra_args
        # print(os.path.join(os.path.dirname(__file__), __file__))

    def exit(self, message="An Error occur"):
        sys.exit(128)

    def skip(self, message='Exiting'):
        sys.exit(0)
        return
        # raise SkipExecutionException(message)

    @property
    def logger(self) -> logger:
        return logger


class SkipExecutionException(Exception):
    pass
