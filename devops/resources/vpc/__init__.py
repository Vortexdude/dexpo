import boto3


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
