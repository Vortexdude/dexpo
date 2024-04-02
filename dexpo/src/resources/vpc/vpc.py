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
        pass

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


def vpc_handler(data: dict) -> dict:
    _vpc_state = {}
    vpc_obj = VpcResource(**data)
    vpcs = vpc_obj.validate()
    if not vpcs:
        print(f"No Vpc found under the name {data['name']} and CIDR block {data['cidr_block']}")
        #  Handle the exiting or skipping form here
    for vpc in vpcs:
        _vpc_state[vpc['VpcId']] = vpc

    return _vpc_state
