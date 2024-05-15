import sys
from dexpo.src.lib.utils import get_class_variable


class DexpoArgParser(object):
    HELPER = '--help'
    APPLY = '--apply'
    DESTROY = '--destroy'

    def __init__(self):
        self.class_var = get_class_variable(self.__class__, True)  # here true means return will be dict
        self.apply = False
        self.destroy = False
        # self.config_file = CONFIG_FILE_PATH + '/config.json'

        if len(sys.argv) <= 1:
            print("\nPlease Supply any arguments")
            self.display_help()
            sys.exit(125)

        for item in sys.argv[1:]:

            if item not in list(self.class_var.values()):
                print("\nUnknown Option - {xd}".format(xd=item))
                self.display_help()
                sys.exit(125)

            if self.HELPER in item:
                self.display_help()
                sys.exit(127)

            if self.APPLY in item:
                self.action = 'apply'
                self.apply = True

            if self.DESTROY in item:
                self.action = 'destroy'
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
