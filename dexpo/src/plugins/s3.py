"""These are docstrings basically a documentation of the module"""
from botocore import errorfactory

from dexpo.settings import trace_route
import boto3
from dexpo.src.lib.models import S3Model
from botocore.client import ClientError
from dexpo.manager import DexpoModule
from dexpo.src.exceptions.main import KeyMissingException

REGION = 'ap-south-1'
extra_args = dict(
    resource_type='dict',
)


class S3Input(S3Model):
    pass


module = DexpoModule(
    base_arg=S3Input,
    extra_args=extra_args,
    module_type='s3'
)
logger = module.logger


class S3Manager:
    SERVICE = 's3'

    def __init__(self, s3_input: S3Input):
        self.s3_input = s3_input
        self.s3_client = boto3.client(self.SERVICE, region_name=REGION)
        self.ec2_resource = boto3.resource(self.SERVICE, region_name=REGION)

    def validate(self):
        response = self.s3_client.list_buckets()['Buckets']
        if not response:
            return {}
        for _buck in response:
            if self.s3_input.name == _buck['Name']:
                return _buck

    def create(self):
        """launch the s3 if the s3 not available"""
        if not self.s3_input.deploy:
            raise KeyMissingException('deploy', 's3')

        try:
            response = self.s3_client.create_bucket(
                Bucket=self.s3_input.name,
                CreateBucketConfiguration={
                    'LocationConstraint': self.s3_input.CreateBucketConfiguration.LocationConstraint
                }
            )
            logger.info(f"Bucket {self.s3_input.name} created Successfully !")
            return response
        except ClientError as e:
            if e.response['ResponseMetadata']['HTTPStatusCode'] == 409:
                logger.warn("Bucket already exists with the same name")

    def delete(self):
        response = self.s3_client.delete_bucket(Bucket=self.s3_input.name, )
        return response


def _validate_s3(s3m: S3Manager):
    logger.debug("validating s3 bucket...")
    bucket = s3m.validate()
    if bucket:
        bucket['CreationDate'] = bucket['CreationDate'].strftime('%m/%d/%Y')
    state_container: dict = module.get_state()
    for s3 in state_container.get('s3', []):
        if 'CreationDate' not in s3.keys() and not bucket:
            module.update_state(data=s3m.s3_input.model_dump())
        if 'CreationDate' not in s3.keys() and bucket:
            logger.info("The S3 bucket might have been deleted from the state.")
            logger.info("Fixing...")
            data = s3m.s3_input.model_dump()
            data['CreationDate'] = bucket['CreationDate']
            module.update_state(data)
        if 'CreationDate' in s3.keys() and not bucket:
            logger.warning("The S3 bucket might have been deleted from the cloud")
            logger.info("Fixing ... ")
            module.update_state(data=s3m.s3_input.model_dump())


def _create_s3(s3m: S3Manager):
    logger.debug("Creating S3........")
    state_container: dict = module.get_state()
    # check if the state having the InstanceId key
    for s3 in state_container.get('s3', []):
        if s3.get('location', ''):
            logger.info('s3 already exist')
            return

    response = s3m.create()
    if response and response['ResponseMetadata']['HTTPStatusCode'] == 200:
        data = s3m.s3_input.model_dump()
        data['location'] = response['Location']
        print(f"{data=}")
        module.update_state(data)


def _delete_s3(s3m: S3Manager):
    logger.debug("deleting s3 bucket ... ")
    state_container: dict = module.get_state()
    for s3 in state_container.get('s3', []):
        if not s3.get('CreationDate', ''):
            logger.warning("Bucket is not launched yet")
            return
        response = s3m.delete()
        if int(response['ResponseMetadata']['RequestId']['HTTPStatusCode']) == 204:
            logger.info("Bucket is deleted successfully!")
            module.update_state(s3m.s3_input.model_dump())


def run_module(action: str, data: dict):
    inp = S3Input(**data)
    s3m = S3Manager(inp)
    if action == 'validate':
        return _validate_s3(s3m)

    elif action == 'create':
        return _create_s3(s3m)

    elif action == 'delete':
        return _delete_s3(s3m)
