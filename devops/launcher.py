import boto3
import time
from aws_kit import Setting


class Base:
    """
    :type vpc_resource: None
    :return: vpc_resource is used for get the boto3 resource
     to associate with other service, and it takes only the vpc
     identifiers like vpc and name to identify the vpc with
     associate with.
    """
    def __init__(self, region: str):
        self.client = boto3.client("ec2", region)
        self.resource = boto3.resource("ec2", region)
        self.vpc_resource = None


class Availability(Base):
    def __init__(self, region=None, vpc_cidr=None, vpc_id=None, vpc_name=None, internet_gateway_name=None, route_table_name=None):
        super().__init__(region)
        self.vpc_cidr = vpc_cidr
        self.vpc_id = vpc_id
        self.vpc_name = vpc_name
        self.route_table_name = route_table_name
        self.internet_gateway_name = internet_gateway_name
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

        elif self.vpc_cidr:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.vpc_cidr]
            })

        elif self.vpc_name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.vpc_name]

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
        if self.internet_gateway_name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.internet_gateway_name]
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
        if self.route_table_name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.route_table_name]
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

    def __init__(self, vpc_cidr=None, vpc_id=None, vpc_name=None, internet_gateway_name=None, route_table_name=None, *args, **kwargs):
        self.ig_id = None

        if not vpc_name and vpc_id:
            print("Please provide any identifier")
            return
        super().__init__(vpc_cidr=vpc_cidr, vpc_id=vpc_id, vpc_name=vpc_name, internet_gateway_name=internet_gateway_name, route_table_name=route_table_name)
        super().vpc()
        super().internet_gateway()
        super().route_table()

    def launch(self):
        """Process starts from here all the logic for launch the infra
           1. Launch the vpc if not available
           2. Launch the Internet gateway if not available

        """

        if not self.vpc_available and self.vpc_cidr:
            self.create_vpc()
        if not self.ig_available:
            self.create_internet_gateway()
            self.attach_ig_to_vpc(self.ig_id)
        if not self.rt_available:
            self.create_route_table()

    def create_vpc(self):
        """launch the vpc if the vpc not available"""

        response = self.client.create_vpc(CidrBlock=self.vpc_cidr)
        vpc_id = response['Vpc']['VpcId']
        self.vpc_resource = self.resource.Vpc(vpc_id)
        self._wait_until_available(self.resource.Vpc(vpc_id), "VPC")
        print(f"VPC {self.vpc_name} Attaching name to the VPC")
        self.vpc_resource.create_tags(
            Tags=[{
                "Key": "Name",
                "Value": self.vpc_name
            }]
        )

    def _wait_until_available(self, resource, resource_name):
        """Wait until the resource is available."""

        resource.wait_until_available()
        print(f"{resource_name} {self.vpc_name} is available.")

    def create_internet_gateway(self):
        response = self.client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.internet_gateway_name
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
            "Value": self.route_table_name
        }])

    def attach_ig_to_vpc(self, ig_id):
        self.vpc_resource.attach_internet_gateway(InternetGatewayId=ig_id)
        print(f"Internet gateway {self.internet_gateway_name} attached to VPC {self.vpc_name} successfully!")


config = Setting()
infrasonic = VpcInfra(**config.__dict__)
infrasonic.launch()