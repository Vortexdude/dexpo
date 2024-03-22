import boto3
from abc import ABCMeta, abstractmethod
from botocore.exceptions import ClientError


# https://stackoverflow.com/questions/8187082/how-can-you-set-class-attributes-from-variable-arguments-kwargs-in-python

class Base:
    """
    :region: None
    :return: vpc_resource is used for get the boto3 resource
     to associate with other service, and it takes only the vpc
     identifiers like vpc and name to identify the vpc with
     associate with.
    """

    def __init__(self, region: str):
        self.region = region
        self.client = boto3.client("ec2", region)
        self.resource = boto3.resource("ec2", region)
        self._resource = None


class Resources(Base):
    def __init__(self):
        super().__init__(region='ap-south-1')

    def vpc(self, _id: str = None):
        return self.resource.Vpc(id)

    def rt(self, _id):
        return self.resource.RouteTable(_id)


class BaseAbstractmethod(metaclass=ABCMeta):

    @abstractmethod
    def validate(self):
        pass

    @abstractmethod
    def to_dict(self, prop: dict):
        pass

    @abstractmethod
    def create(self):
        pass

    @abstractmethod
    def delete(self):
        pass
