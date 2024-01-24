import boto3
import time
REGION = "ap-south-1"
APP_NAME = "boto3-sandbox"


client = boto3.client("ec2", REGION)
resource = boto3.resource("ec2", REGION)


class VpcInfra:
    """
    Args:
        cidr: str to check the vpc is available or not in the availability zone
    returns:
        self.vpc_available: bool True if available else False

    """
    def __init__(self, cidr: str = None, vpc_id: str = None):
        self.cidr = cidr
        self.vpc_id = vpc_id
        self.filters = []
        self.client = boto3.client("ec2", REGION)
        self.resource = boto3.resource("ec2", REGION)
        self.vpc_available = self.check_availability

    @property
    def check_availability(self):
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

        else:
            return False

        response = self.client.describe_vpcs(Filters=self.filters)
        return True if response['Vpcs'] else False


def create_vpc(cidr, name=None):
    responce = client.create_vpc(
        CidrBlock=cidr,
    )

    status = responce['Vpc']['State']
    id = responce['Vpc']['VpcId']


    while True:
        if status.lower() == 'pending':
            vpcInit = resource.Vpc(id)
            print("Launching VPC . . . ")
            status = vpcInit.state
            time.sleep(1)
        else:
            print("VPC Lunached successfully!")
            break


infrasonic: VpcInfra = VpcInfra(vpc_id="vpc-08a62c4b70250463b")

print(infrasonic.vpc_available)
