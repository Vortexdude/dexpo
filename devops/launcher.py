import boto3
import time

REGION = "ap-south-1"
APP_NAME = "boto3-sandbox"

client = boto3.client("ec2", REGION)
resource = boto3.resource("ec2", REGION)


def add_tags(vpc_resource, name:str):
    vpc_resource.create_tags(
        Tags=[{
            "Key": "Name",
            "Value": name
        }]
    )
    vpc_resource.wait_until_available()


class Base:
    def __init__(self):
        self.client = boto3.client("ec2", REGION)
        self.resource = boto3.resource("ec2", REGION)
        self.vpc_resource = None


class Availability(Base):
    def __init__(self, cidr: str = None, vpc_id: str = None, name: str = None):
        super().__init__()
        self.cidr = cidr
        self.vpc_id = vpc_id
        self.name = name
        self.filters = []
        self.tags = []
        self.vpc_available = False
        self.ig_available = False
        self.rt_available = False
        self.ig_id = None

    def vpc(self):
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""

        if self.vpc_id:
            self.filters.append({
                "Name": "vpc-id",
                "Values": [self.vpc_id]
            })

        elif self.cidr:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.cidr]
            })

        elif self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name]

            })
        else:
            print("Something not parsed into the function")

        response = self.client.describe_vpcs(Filters=self.filters)
        self.filters = []
        if response['Vpcs']:
            if not self.vpc_id:
                self.vpc_id = response['Vpcs'][0]['VpcId']
                self.vpc_resource = self.resource.Vpc(self.vpc_id)
            self.vpc_available = True
            print("VPC Available")

        else:
            print("VPC Not Available")

    def internet_gateway(self):
        if self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name+'-ig']
            })
        response = self.client.describe_internet_gateways(Filters=self.filters)

        self.filters = []
        if response['InternetGateways']:
            self.ig_available = True
            self.ig_id = response['InternetGateways'][0]['InternetGatewayId']
            print("IG Available")
        else:
            print("IG Not Available")

    def route_table(self):
        if self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name+'-rt']
            })
        response = self.client.describe_route_tables(Filters=self.filters)
        self.filters = []
        if response['RouteTables']:
            self.rt_available = True
            print("RT Available")
        else:
            print("RT Not Available")


class VpcInfra(Availability):
    """
    Args:
        cidr: str to check the vpc is available or not in the availability zone
    returns:
        self.vpc_available: bool True if available else False
    REFS = https://stackoverflow.com/questions/47329675/boto3-how-to-check-if-vpc-already-exists-before-creating-it

    """

    def __init__(self, cidr: str = None, vpc_id: str = None, name: str = None):
        self.ig_id = None

        if not name and vpc_id:
            print("Please provide any identifier")
            return
        super().__init__(cidr=cidr, vpc_id=vpc_id, name=name)
        super().vpc()
        super().internet_gateway()
        super().route_table()

    def launch(self):
        """Process starts from here all the logic for launch the infra
           1. Launch the vpc if not available
           2. Launch the Internet gateway if not available

        """

        if not self.vpc_available and self.cidr:
            self.create_vpc()
        if not self.ig_available:
            self.create_internet_gateway()
            self.attach_ig_to_vpc(self.ig_id)
        if not self.rt_available:
            self.create_route_table()

    def create_vpc(self):
        """
        launch the vpc if the vpc not available
        """

        _res = self.client.create_vpc(CidrBlock=self.cidr)
        _state = _res['Vpc']['State']
        _id = _res['Vpc']['VpcId']
        self.vpc_resource = self.resource.Vpc(_id)
        while True:
            if _state.lower() == "pending":
                print("Launching VPC . . . ")
                time.sleep(1)
                self.vpc_resource = self.resource.Vpc(_id)
                _state = self.vpc_resource.state
            else:
                print("VPC Launched successfully!")
                self.vpc_available = True
                self.vpc_id = _id
                break
        if self.name:
            print(f"VPC {self.name} Attaching name to the VPC")
            add_tags(self.vpc_resource, self.name)
            print(f"VPC {self.name} attached to VPC Successfully")

        else:
            print("VPC is already Exist")

    def create_internet_gateway(self):
        response = self.client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.name + '-ig'
                }]
            }]
        )
        if response['InternetGateway']:
            print("Internet Gateway Created Successfully!")
            _ig = response['InternetGateway']['InternetGatewayId']
            self.ig_id = _ig
        else:
            print("There is an error")

    def create_route_table(self):
        routeTable = self.vpc_resource.create_route_table()
        route = routeTable.create_route(
            DestinationCidrBlock="0.0.0.0/0",
            GatewayId=self.ig_id
        )
        routeTable.create_tags(Tags=[{
            "Key": "Name",
            "Value": self.name + "-rt"
        }])

    def attach_ig_to_vpc(self, ig_id):
        self.vpc_resource.attach_internet_gateway(InternetGatewayId=ig_id)
        print(f"Internet gateway {self.name}-ig attached to VPC {self.vpc_id} successfully!")


infrasonic = VpcInfra(name="Boto3-testing", cidr="192.168.0.0/16")
# print(infrasonic.create_route_table())
infrasonic.launch()
