import requests

cidr = '192.168.1.0/24'

ulr = f'https://ec2.amazonaws.com/?Action=CreateVpc&CidrBlock={cidr}&TagSpecification.1.ResourceType=vpc&TagSpecification.1.Key=vpc&TagSpecification.1.Value=example&AUTHPARAMS'

url = "https://ec2.amazonaws.com/?Action=CreateVpc&AUTHPARAMS"

url = "https://ec2.amazonaws.com/?Action=CreateVpc&CidrBlock=192.168.1.0/24&AUTHPARAMS"

responce = requests.get(url=url)
print(responce)