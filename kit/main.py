import os
from lib.utils import AwsKit










s3 = AwsKit('s3')
bucket_name = 'butena'
object_name = 'private_keys/butena'
file_name = '/home/ncs/opt/butena'
# s3.download_file_from_s3(bucket_name, object_name, file_name)
# os.chmod(file_name, 0o600)


filename = '/home/ncs/opt/workspace/vortexdude/dexpo/dexpo/state.json'
s3.upload_file_to_s3(bucket_name, file_name, 'states/state.json')