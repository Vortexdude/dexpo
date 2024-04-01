import boto3
from abc import ABCMeta, abstractmethod
import json


class State:
    def __init__(self, resources=None):
        self.resources = resources if resources else {}

    def add_resource(self, resource_id, resource_data):
        self.resources[resource_id] = resource_data

    def remove_resource(self, resource_id):
        if resource_id in self.resources:
            del self.resources[resource_id]

    def get_resource(self, resource_id):
        return self.resources.get(resource_id)

    def save_to_file(self, file_path):
        with open(file_path, 'a+') as file:
            file.seek(0)
            existing_data = json.load(file) if file.read(1) else {}  # Read existing data if file is not empty
            existing_data.update(self.resources)
            file.seek(0)
            json.dump(existing_data, file, indent=4)

    @classmethod
    def load_from_file(cls, file_path):
        with open(file_path, 'r') as file:
            resources = json.load(file)
        return cls(resources)


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
