import sys
import os
from dexpo.src.lib.utils import get_class_variable, CONFIG_FILE_PATH


class DexpoArgParser(object):
    HELPER = '--help'
    APPLY = '--apply'
    DESTROY = '--destroy'

    def __init__(self):
        self.class_var = get_class_variable(self.__class__, True)
        self.apply = False
        self.destroy = False
        self.config_file = CONFIG_FILE_PATH + '/config.json'

        for xd in sys.argv[1:]:
            if xd not in list(self.class_var.values()):
                print("\nUnknown Option - {xd}".format(xd=xd))
                self.display_help()
                sys.exit(125)

        for item in sys.argv[1:]:

            if self.HELPER in item:
                self.display_help()
                sys.exit(127)
            if self.APPLY in item:
                print("Applying.....")
                self.apply = True

            if self.DESTROY in item:
                print("Destroying.....")
                self.destroy = True

    @staticmethod
    def display_help():
        print("""

    usage: main.py [--help] [--foo FOO] [bar [bar ...]]

    Description. Manage the AWS Cloud infrastructure using boto3.

    positional arguments:
      file      PATH         

    optional Description:
      --help \t show this help message and exit
      --apply \t For done the changes and launch the infrastructure using boto3
      --Destroy\t destroy the infra


    All is well that ends.
    Thanks for Reading...""")
