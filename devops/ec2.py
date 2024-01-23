import boto3
import botocore.exceptions
from utils import logger

VPC_ID = "vpc-08a62c4b70250463b"
SECURITY_GROUP = "sg-07336c13675c532a7"
AMI_ID = "ami-0a7cf821b91bcccbc"
TYPE = "t2.micro"
SSH_KEY = "key-08985a509dc836907"
APP_NAME = "boto3-sandbox"
REGION = "ap-south-1"

sg_ingress_rules = [
    {
        'FromPort': 22,
        'IpProtocol': 'tcp',
        'ToPort': 22,
        'UserIdGroupPairs': [
            {
                'Description': 'SSH acces to the server',
                'GroupId': '{group_id}'
            }
        ]
    }
]


class AwsInfrastructure():
    """
    class `AwsInfrastructure` is used to create, modify and delete Aws resource
    """

    def __init__(self, region, vpc, ):
        self.region = region
        self.vpc = vpc
        self.client = boto3.client('ec2', self.region)
        self.resource = boto3.resource('ec2', self.region)

    def create_security_group(self, name: str = None, description: str | None = None) -> str:
        """For creating security Groups"""

        if not name:
            name =  f'{name}-sg'

        if not description:
            description =  f'{APP_NAME}-sg is used for automation testing' 

        try:
            secGroup = self.resource.create_security_group(
                Description = description,
                GroupName = name,
                VpcId = self.vpc
            )
            print(secGroup)
        except botocore.exceptions.ClientError:
            logger.error("Security Group already exist")
            print("Security Group already exist")
            return
        try:
            secGroup.authorize_ingress(
                IpPermissions = [
                    {
                        'FromPort': 22,
                        'ToPort': 22,
                        'IpProtocol': 'tcp',
                        'IpRanges': [
                            {
                                'CidrIp': '{}/0'.format('0.0.0.0'),
                                'Description': 'SSH Access'

                            }
                        ]
                    }
                ]
            )
            secGroup.create_tags(Tags=[{'Key':"Name", "Value": "sgName"}])
            logger.info(f"Security Group created Succesfully! - details {secGroup}")
            print("Security Group Created succesfully!")
            self.secGroup = secGroup

        except botocore.exceptions:
            logger.error("Port is already defined in the security group")
            print("Port is already exist in the security group")

    def create_internet_gateway(self, igName):
        """Creating internet gateway"""

        igInit = self.client.create_internet_gateway(
            TagSpecifications=[
                {'ResourceType': 'internet-gateway',
                    'Tags': [{"Key": "Name", "Value": igName}]}, ]
        )
        igId = igInit["InternetGateway"]["InternetGatewayId"]
        self.client.attach_internet_gateway(InternetGatewayId=igId, VpcId=self.vpc)
        # self.vpc.attach_internet_gateway(InternetGatewayId=igId)
        self.igId = igId

    def create_vpc(self, cidr_block: str, vpc_name:str):
        """For creating vpc"""

        vpcInit = self.client.create_vpc(CidrBlock = cidr_block)

        logger.info("VPC created succesfully!")
        print(vpcInit)
        return
        vpc = self.resource.Vpc(vpcInit["Vpc"]["vpcName"])
        vpc.create_tags(Tags=[{"Key": "name", "Value": vpc_name}])
        logger.info("Added the tags in the vpc")
        vpc.wait_untill_available()
        self.vpc = vpc

    def create_route_table(self):
        self.client.create_route_table()

infra = AwsInfrastructure(region=REGION, vpc=VPC_ID)
infra.create_vpc('192.168.1.0/24', "boto3-testing")
# infra.create_security_group(name="boto3-testing")
# infra.create_internet_gateway(igName="boto3-testing")
infra.create_