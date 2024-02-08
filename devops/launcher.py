from devops.models.config import RootModel
from devops.resources import Base
from devops.resources.vpc.main import Vpc
from devops.resources.vpc.route_table import RouteTable
from devops.resources.vpc.intenet_gateway import InternetGateway
from devops.resources.vpc.subnet import Subnet
from devops.resources.vpc.security_group import SecurityGroup
from devops.utils import Utils, DexColors
from devops.resources.const import _EC2, _VPC, _SUBNET, _ROUTE_TABLE, _SECURITY_GROUP, _INTERNET_GATEWAY, DISPLAY_TEXT

dex_color = DexColors()



CONFIG_FILE = 'config.json'
COMMAND = ''
RESOURCE_COUNT: int = 0
# convert the json into dictionary
_json = Utils.read_json(CONFIG_FILE)

# pass the data into the Model fto get the accurate data
config = RootModel(**_json)
RESULT = []


class BaseVpcInit:
    def __init__(self):
        self.vpc_id = None
        self.ig_id = None
        self.rt_id = None
        self.vpc_available = False
        self.ig_available = False
        self.rt_available = False
        self.vpc_resource = None


class VpcMaster(BaseVpcInit, Base):
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
            name: str = None,
            state: str = None,
            dry_run: bool = False,
            region: str = None,
            cidr_block: str = None,
            route_table: dict = None,
            internet_gateway: dict = None,
            subnets: list[dict] = None,
            security_groups: list[dict] = None,
            *args, **kwargs):

        super().__init__()
        super(Base, self).__init__()
        self._subnets_availability = []
        self.subnets = subnets
        self.security_groups = security_groups
        self.internet_gateway = internet_gateway
        self.route_table = route_table
        self.state = state
        self.name = name
        """Validating the VPC"""

        self._vpc = Vpc(vpc_name=name, state=state, dry_run=dry_run, vpc_cidr=cidr_block, region=region)
        self._vpc_data = self._vpc.validate()
        self._vpc_data['name'] = self.name
        self._vpc_data['type'] = "vpc"
        RESULT.append(self._vpc_data)

        if self._vpc_data['available']:
            self.vpc_id = self._vpc_data['id']
            self.vpc_resource = self._vpc_data['resource']
        else:
            self.vpc_resource = None
            self.vpc_id = ''

        """Validating the Internet Gateway"""

        self._ig = InternetGateway(
            name=internet_gateway.get('name', ''),
            state=internet_gateway.get('state', ''),
            dry_run=internet_gateway.get('dry_run', ''),
            region=internet_gateway.get('region', '')
        )
        self._ig_data = self._ig.validate()
        self._ig_data['name'] = self.internet_gateway['name']
        self._ig_data['type'] = "internet_gateway"
        RESULT.append(self._ig_data)

        if self._ig_data['available']:
            self.ig_id = self._ig_data['id']
            self.ig_resource = self._ig_data['resource']
        else:
            self.ig_resource = None
            self.ig_id = ""

        """Validating the route table"""

        self._rt = RouteTable(
            name=route_table.get('name', ''),
            state=route_table.get('state', ''),
            dry_run=route_table.get('dry_run', '')
        )
        self._rt_data = self._rt.validate()
        self._rt_data['name'] = self.route_table['name']
        self._rt_data['type'] = 'route_table'
        RESULT.append(self._rt_data)

        if self._rt_data['available']:
            self.rt_id = self._rt_data['id']
            self.rt_resource = self._rt_data['resource']
        else:
            self.rt_resource = None
            self.rt_id = ""

        """Validating the Subnets"""

        self.subnets_data = []
        for subnet in self.subnets:
            self._sb = Subnet(**subnet)
            _sb_data = self._sb.validate()

            if _sb_data['available']:
                sb_id = _sb_data['id']
                sb_resource = _sb_data['resource']
            else:
                sb_resource = None
                sb_id = ""
            self.subnets_data.append({subnet['name']: [sb_resource, sb_id, 'subnet'], "handler": self._sb})

        RESULT.append(self.subnets_data)

        """Validating Security Group"""
        self.security_group_data = []
        for security_group in self.security_groups:
            self._sg = SecurityGroup(**security_group)
            _sg_data = self._sg.validate()

            if _sg_data['available']:
                sg_id = _sg_data['id']
                sg_resource = _sg_data['resource']
            else:
                sg_id = _sg_data['id']
                sg_resource = _sg_data['resource']
            self.security_group_data.append(
                {security_group['name']: [sg_resource, sg_id, 'security_group'], "handler": self._sg})

        RESULT.append(self.security_group_data)

    def launch(self):

        if not self._vpc_data['available'] and self.state == "present":
            self._vpc_data = self._vpc.create()
            print(self._vpc_data['message'])
            if self._vpc_data['status']:
                self.vpc_resource = self._vpc_data['resource']
                self.vpc_id = self._vpc_data['resource_id']

        if not self._ig_data['available'] and self.internet_gateway['state'] == "present":
            self._ig_data = self._ig.create(self.vpc_resource)
            print(self._ig_data['message'])
            if self._ig_data['status']:
                self.ig_resource = self._ig_data['resource']
                self.ig_id = self._ig_data['resource_id']

        if not self._rt_data['available'] and self.route_table['state'] == "present":
            self._rt_data = self._rt.create(self.vpc_resource, self.ig_id)
            print(self._rt_data['message'])
            if self._rt_data['status']:
                self.rt_resource = self._rt_data['resource']
                self.rt_id = self._rt_data['resource_id']

        # going through the subnet validate data loop (form validate method) that contains
        # the status and resource of the subnet
        # then check availability of the subnet is there or not if not then create it

        for i in range(len(self.subnets_data)):
            if not self.subnets_data[i][self.subnets[i]['name']][0] and self.subnets[i]['state'] == "present":
                sb_data = self.subnets_data[i]["handler"].create(self.vpc_resource, self.rt_resource)
                self.subnets_data[i][self.subnets[i]['name']][0] = sb_data['resource']
                self.subnets_data[i][self.subnets[i]['name']][1] = sb_data['resource_id']
                print(sb_data['message'])

        for j in range(len(self.security_group_data)):
            if not self.security_group_data[j][self.security_groups[j]['name']][0] and self.security_groups[j]['state'] == "present":
                sg_data = self.security_group_data[j]["handler"].create(self.vpc_id)
                self.security_group_data[j][self.security_groups[j]['name']][0] = sg_data['resource']
                self.security_group_data[j][self.security_groups[j]['name']][1] = sg_data['resource_id']
                print(sg_data['message'])

    def delete(self):
        """For delete the AWS resources Sequentially"""

        """Delete the internet gateway first"""
        ig_delete_response = self._ig.delete(self.vpc_resource, self.vpc_id)
        print(ig_delete_response['message'])

        """ Delete the subnets """
        for i in range(len(self.subnets_data)):
            sb_delete_response = self.subnets_data[i]["handler"].delete(
                self.subnets_data[i][self.subnets[i]['name']][0])
            print(sb_delete_response['message'])

        """ Delete the Route Tables """
        rt_delete_response = self._rt.delete(self.rt_resource)
        print(rt_delete_response['message'])

        """ Delete the Security Groups """
        for i in range(len(self.security_group_data)):
            sg_delete_response = self.security_group_data[i]["handler"].delete(
                self.security_group_data[i][self.security_groups[i]['name']][0])
            print(sg_delete_response['message'])

        """ Delete the VPC """
        vpc_delete_response = self._vpc.delete()
        print(vpc_delete_response['message'])


class Ec2Master(Base):
    def __init__(
            self,
            name: str = None,
            instance_type: str = None,
            ami: str = None,
            subnet: str = None,
            key_file: str = None,
            region: str = 'ap-south-1',
            state: str = None,
            dry_run: bool = False

    ):
        self.region = region
        self.name = name
        self.instance_type = instance_type
        self.ami = ami
        self.subnet = subnet
        self.key_file = key_file
        self.state = state
        self.dry_run = dry_run
        super().__init__(region='ap-south-1')

    def validate(self):
        pass

    def launch(self):
        pass

    def delete(self):
        pass


def runner(*args, **kwargs):
    global RESOURCE_COUNT
    for _vdata in kwargs['vpc']:
        vpc_master = VpcMaster(**_vdata)
        if COMMAND.lower() == 'apply':
            for row in RESULT:
                if isinstance(row, list):
                    _tmp_text = ""
                    for item in row:
                        # item = {'boto3-testing-sg': [None, None, "type"], 'handler': <devops.resources.vpc.security_group.SecurityGroup object at 0x7f9ccafa5c50>}
                        resource_name = list(item.keys())[0]
                        resource_availability = item[resource_name][0]
                        resource_id = item[resource_name][1]
                        resource_type: str = item[resource_name][2].lower()

                        if resource_availability:  # skip loop when resource available
                            continue
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

                    print(dex_color.dprint(DexColors.Color.SUCCESS, _tmp_text))

                else:
                    if not row['available']:
                        RESOURCE_COUNT += 1
                        resource_type = row['type'].lower()
                        _tmp_text = ''
                        resource_mapping = {
                            "vpc": (_VPC, vpc_master.name, vpc_master.vpc_id),
                            "route_table": (_ROUTE_TABLE, row['name'], row['id']),
                            "internet_gateway": (_INTERNET_GATEWAY, row['name'], row['id'])
                        }
                        _tmp_text += resource_mapping[resource_type][0]
                        _tmp_text += DISPLAY_TEXT.format(
                            name=resource_mapping[resource_type][1],
                            id=resource_mapping[resource_type][2] if resource_mapping[resource_type][
                                2] else "Known after apply",
                            text=f"Adding new {resource_type.capitalize()}"
                        )

                        print(dex_color.dprint(DexColors.Color.SUCCESS, _tmp_text))

        # if RESOURCE_COUNT <= 0:
        #     print(f'Nothing to do with the Infrastructure')
        #     return
        # print(f'Going to Launch {RESOURCE_COUNT} Resources')

        if COMMAND.lower() == 'apply':
            action = input('Want to Launch .... [Yes/No] ')
            if action.lower() == 'yes':
                vpc_master.launch()
            else:
                print("Exiting ....")

        if COMMAND.lower() == 'destroy':
            action = input('Want to Destroy .... [Yes/No] ')
            if action.lower() == 'yes':
                vpc_master.delete()
            else:
                print("Exiting ....")

    for ec2_data in kwargs['ec2']:

        return
        ec2_master = Ec2Master(**ec2_data)
        if COMMAND.lower() == 'apply':
            action = input('Want to Launch .... [Yes/No] ')
            if action.lower() == 'yes':
                ec2_master.launch()
            else:
                print("Exiting ....")

        if COMMAND.lower() == 'destroy':
            action = input('Want to Destroy .... [Yes/No] ')
            if action.lower() == 'yes':
                ec2_master.delete()
            else:
                print("Exiting ....")


def run(command: str):
    global COMMAND
    COMMAND = command
    runner(**config.model_dump())
    # print(_json)
