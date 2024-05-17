from lib.utils import AwsKit
from dexpo.settings import logger

s3 = AwsKit('s3')


def upload_to_s3(*args, **kwargs):
    logger.info("uploading state file to s3.")
    return s3.upload_file_to_s3(*args, **kwargs)


def file_exists(*args, **kwargs):
    logger.info("Validating the file in the s3")
    return s3.check_object(*args, **kwargs)


def download_state(*args, **kwargs):
    logger.info("Downloading State file from the S3")
    return s3.download_file_from_s3(*args, **kwargs)
