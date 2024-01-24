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


class VpcInfra:
    """
    Args:
        cidr: str to check the vpc is available or not in the availability zone
    returns:
        self.vpc_available: bool True if available else False
    REFS = https://stackoverflow.com/questions/47329675/boto3-how-to-check-if-vpc-already-exists-before-creating-it

    """

    def __init__(self, cidr: str = None, vpc_id: str = None, name: str = None):
        self.cidr = cidr
        self.vpc_id = vpc_id
        self.name = name
        self.filters = []
        self.tags = []
        self.vpc_stat = None
        self.client = boto3.client("ec2", REGION)
        self.resource = boto3.resource("ec2", REGION)
        self.vpc_available = self.check_vpc_availability
        self.ig_available = self.check_ig_availability

    @property
    def check_vpc_availability(self):
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
            return False

        response = self.client.describe_vpcs(Filters=self.filters)
        self.filters = []
        if response['Vpcs']:
            self.vpc_id = response['Vpcs'][0]['VpcId']
            return True

        else:
            return False

    @property
    def check_ig_availability(self):
        if self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name+'-ig']
            })
        response = self.client.describe_internet_gateways(Filters=self.filters)
        self.filters = []
        return True if response['InternetGateways'] else False

    def create_vpc(self):
        """
        launch the vpc if the vpc not available
        """
        if not self.vpc_available and self.cidr:
            _res = self.client.create_vpc(CidrBlock=self.cidr)
            _state = _res['Vpc']['State']
            _id = _res['Vpc']['VpcId']
            vpc_stat = resource.Vpc(_id)
            while True:
                if _state.lower() == "pending":
                    print("Launching VPC . . . ")
                    time.sleep(1)
                    vpc_stat = resource.Vpc(_id)
                    _state = vpc_stat.state
                else:
                    print("VPC Launched successfully!")
                    self.vpc_available = True
                    break
            if self.name:
                print(f"Name {self.name} Attaching name to the VPC")
                add_tags(vpc_stat, self.name)
                print(f"Name {self.name} attached to VPC Successfully")

        else:
            print("VPC is already Exist")

        if not self.ig_available:
            vpc_stat = self.resource.Vpc(self.vpc_id)
            self.create_internet_gateway(vpc_stat)

    def create_internet_gateway(self, vpc):
        response = self.client.create_internet_gateway(
            TagSpecifications=[{
                "ResourceType": "internet-gateway",
                "Tags": [{
                    "Key": "Name",
                    "Value": self.name + '-ig'
                }]
            }]
        )
        print("Internet Gateway Created Successfully!")
        _ig = response['InternetGateways']['InternetGatewayId']
        vpc.attach_internet_gateway(InternetGatewayId=_ig)
        print(f"Attached internet gateway f{self.name}-ig to VPC {self.vpc_id}")


infrasonic = VpcInfra(name="Boto3-testing")

print(infrasonic.check_ig_availability)
