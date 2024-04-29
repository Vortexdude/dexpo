import boto3
from .test import DexpoModule
from pydantic import BaseModel, ValidationError


result = dict()


class VpcInput(BaseModel):
    name: str
    deploy: bool
    dry_run: bool
    region: str
    CidrBlock: str


class VpcManager:
    def __init__(self, vpc_input: VpcInput):
        self.vpc_input = vpc_input
        self.validate_data()
        self.ec2_client = boto3.client("ec2", region_name=self.vpc_input.region)
        self.ec2_resource = boto3.resource('ec2', region_name=self.vpc_input.region)

    def validate_data(self):
        try:
            self.vpc_input = VpcInput(**self.vpc_input.dict())
        except ValidationError as e:
            raise e

    def create(self) -> tuple:
        """launch the vpc if the vpc not available"""
        if self.vpc_input.deploy:
            response = self.ec2_client.create_vpc(CidrBlock=self.vpc_input.CidrBlock)
            vpc_resource = self.ec2_resource.Vpc(response['Vpc']['VpcId'])
            vpc_resource.wait_until_available()
            vpc_resource.create_tags(
                Tags=[{
                    "Key": "Name",
                    "Value": self.vpc_input.name
                }]
            )  # adding name to the VPC

            result['status'] = f"{self.vpc_input.name} VPC Created Successfully!"
            return response, vpc_resource
        else:
            return {}, None

    def validate(self) -> dict:
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""
        filters = []
        if self.vpc_input.CidrBlock:
            filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.vpc_input.CidrBlock]
            })

        elif self.vpc_input.name:
            filters.append({
                "Name": "tag:Name",
                "Values": [self.vpc_input.name]

            })
        else:
            return {'message': "For search the vpc need to give Identification"}

        response = self.ec2_client.describe_vpcs(Filters=filters)
        if not response['Vpcs']:
            return {}

        return response['Vpcs'][0]

    def delete(self):
        pass


def run_module(action: str, data: dict):
    result = dict(
        changed=False
    )

    module = DexpoModule(
        base_arg=VpcInput,
        extra_args=None
    )
    inp = VpcInput(**data)
    vpc = VpcManager(inp)
    if action == 'validate':
        response = vpc.validate()
        if 'message' in response:
            module.logger.debug(response['message'])  # also skip the
            return
        if 'VpcId' not in response:
            module.logger.debug(f"No Vpc found under the name {data['name']} and CIDR block {data['CidrBlock']}")

        else:
            resource = vpc.ec2_resource.Vpc(response['VpcId'])
            response.update({'resource': resource})
            result['vpc'] = response
            result['vpc']['resource'] = resource
            result['changed'] = True

        return result

    elif action == 'create':
        response, resource = vpc.create()
        if not response:
            result['changed'] = False
        else:
            result['vpc'] = response
            result['vpc']['resource'] = resource

        return result
    if action == 'delete':
        vpc.delete()
