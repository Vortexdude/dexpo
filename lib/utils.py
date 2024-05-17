import boto3
from botocore.exceptions import NoCredentialsError, ClientError


class AwsKit:
    def __init__(self, service):
        if not AwsVerify.verify():
            raise Exception("Unable to locate credentials.")

        self.client = boto3.client(service)
        self.resource = boto3.resource(service)

    def download_file_from_s3(self, bucket, key, filename=None):
        if filename is None:
            filename = key

        self.client.download_file(bucket, key, filename)

    def upload_file_to_s3(self, bucket, filename, key):
        try:
            with open(filename, 'rb') as f:
                contents = f.read()

            self.client.put_object(
                Body=bytes(contents),
                Bucket=bucket,
                Key=key,
                ContentType='text/json',
                ContentDisposition='inline'
            )
            print(f"Uploading file {filename} ...")
        except ClientError as e:
            raise Exception(e)

    def check_object(self, bucket, object_name):
        try:
            self.resource.Object(bucket, object_name).load()
        except ClientError as e:
            if e.response['Error']['Code'] == "404":
                return False
            else:
                raise
        else:
            return True


class AwsVerify:
    @staticmethod
    def verify():
        sts = boto3.client('sts')
        try:
            sts.get_caller_identity()
            return True
        except NoCredentialsError:
            return False
