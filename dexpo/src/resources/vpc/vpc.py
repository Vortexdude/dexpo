from dexpo.src.resources.main import Base, BaseAbstractmethod


class VpcResource(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=False, dry_run=False, cidr_block=None, region='ap-south-1'):
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.cidr_block = cidr_block
        self.region = region
        self.filters = []
        super().__init__(region=region)

    def create(self):
        """launch the vpc if the vpc not available"""

        if self.state == "present":
            response = self.client.create_vpc(CidrBlock=self.cidr_block)
            vpc_id = response['Vpc']['VpcId']
            self._resource = self.resource.Vpc(vpc_id)
            self._resource.wait_until_available()
            self._resource.create_tags(
                Tags=[{
                    "Key": "Name",
                    "Value": self.name
                }]
            )  # adding name to the VPC

            print(f"Vpc {self.name} Created Successfully!")

    def validate(self) -> list:
        """Check the availability of the vpc with certain parameter like cidr, vpc_id"""

        if self.cidr_block:
            self.filters.append({
                'Name': 'cidr-block-association.cidr-block',
                'Values': [self.cidr_block]
            })

        elif self.name:
            self.filters.append({
                "Name": "tag:Name",
                "Values": [self.name]

            })
        else:
            print("Something not parsed into the function")

        response = self.client.describe_vpcs(Filters=self.filters)
        return response['Vpcs']

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass

    def xResource(self, id: str):
        return self.resource.Vpc(id)

def vpc_validator(data: dict) -> dict:
    _vpc_state = {}
    vpc_obj = VpcResource(**data)
    vpcs = vpc_obj.validate()
    if not vpcs:
        print(f"No Vpc found under the name {data['name']} and CIDR block {data['cidr_block']}")
        #  Handle the exiting or skipping form here
    for vpc in vpcs:
        _vpc_state[data['name']] = vpc

    return _vpc_state


def create_vpc(data: dict):
    vpc_obj = VpcResource(**data)
    vpc_obj.create()
