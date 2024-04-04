import boto3
from abc import ABCMeta, abstractmethod


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


class BaseAbstractmethod(metaclass=ABCMeta):

    @abstractmethod
    def validate(self, *args, **kwargs):
        pass

    @abstractmethod
    def to_dict(self, *args, **kwargs):
        pass

    @abstractmethod
    def create(self, *args, **kwargs):
        pass

    @abstractmethod
    def delete(self, *args, **kwargs):
        pass
