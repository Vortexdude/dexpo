import settings
from devops.models.config import RootModel
from devops.resources import Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
from devops.resources.vpc.security_group import SecurityGroup
from devops.lib.utils import Utils, DexColors
import os


dex_color = DexColors()

CONFIG_FILE = '../env/config.json'

STATE_FILE_NAME = 'state.json'
COMMAND = ''
RESOURCE_COUNT: int = 0
# convert the json into dictionary
_json = Utils.read_json(CONFIG_FILE)

# pass the data into the Model fto get the accurate data
config = RootModel(**_json)
RESULT = []


STATE_FILE = os.path.abspath(STATE_FILE_NAME)


class VpcMaster(Base):
    """
    Launch and validate the vpc infrastructure using boto3.
    it inherits some methods and parameters from Availability class that will ensure
    the services are already launched or not if just create an instance of the class
    it just validate the vpc service is already exist or not.

    :type vpc_cidr: string
    :param vpc_cidr: cidr is required to Launch the vpc in that

    :type vpc_id: string
    :param vpc_id: its optional for already exist the vpc or not

    REFS = https://stackoverflow.com/questions/47329675/boto3-how-to-check-if-vpc-already-exists-before-creating-it
    :return: check the services already exist or not
    """

    def __init__(
            self,
            vpc: dict = None,
            route_table: dict = None,
            internet_gateway: dict = None,
            subnets: list[dict] = None,
            security_groups: list[dict] = None,
            *args, **kwargs):

        super().__init__(region='ap-south-1')
        self.security_groups = security_groups
        self.internet_gateway = internet_gateway
        self.subnets = subnets
        self.route_table = route_table
        self.vpc = vpc
        self.moduleStates = {}
        """Validating the VPC"""

        self.moduleVpc = Vpc(**vpc)
        self.moduleVpc.validate()
        self.moduleStates.update({self.vpc['name']: self.moduleVpc.to_dict(vpc)})

        """Validating the Internet Gateway"""

        self.moduleIg = InternetGateway(**internet_gateway)
        self.moduleIg.validate()
        self.moduleStates.update({self.internet_gateway['name']: self.moduleIg.to_dict(internet_gateway)})

        """Validating the route table"""

        self.moduleRt = RouteTable(**route_table)
        self.moduleRt.validate()
        self.moduleStates.update({self.route_table['name']: self.moduleRt.to_dict(route_table)})

        """Validating the Subnets"""

        for subnet in subnets:
            self.moduleSbn = Subnet(**subnet)
            self.moduleSbn.validate()
            self.moduleStates.update({subnet['name']: self.moduleSbn.to_dict(subnet)})

        """Validating Security Group"""

        for security_group in security_groups:
            self.moduleSg = SecurityGroup(**security_group)
            self.moduleSg.validate()
            self.moduleStates.update({security_group['name']: self.moduleSg.to_dict(security_group)})

        Utils.write_to_file('state.json', self.moduleStates)


    def _store_state(self):
        global STATE_FILE


    def launch(self):
        for module in self.moduleStates:
            print(module)


    def delete(self):
        """For delete the AWS resources Sequentially"""
        pass


def runner(*args, **kwargs):
    logger = settings.logger
    vpcs = settings.vpcs
    for _vdata in vpcs:
        vpc_master = VpcMaster(**_vdata)


def run(command: str):
    global COMMAND
    COMMAND = command
    runner(**config.model_dump())
    # print(_json)
