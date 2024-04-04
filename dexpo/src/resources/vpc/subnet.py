from dexpo.src.resources.main import Base, BaseAbstractmethod


class Subnet(Base, BaseAbstractmethod):

    def __init__(self, name=None, state=None, dry_run=False, cidr=None, route_table=None, region='ap-south-1', zone='a'):
        super().__init__(region=region)
        self.route_table = route_table
        self.name = name
        self.state = state
        self.dry_run = dry_run
        self.zone = zone
        self.cidr = cidr

    def validate(self) -> list:
        response = self.client.describe_subnets(
            Filters=[
                {
                    'Name': "tag:Name",
                    'Values': [
                        self.name,
                    ],
                },
            ],
        )

        return response['Subnets']

    def create(self):
        pass

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def subnet_validator(data: dict) -> dict:
    _subnet_state = {}
    sb_obj = Subnet(**data)
    subnets = sb_obj.validate()
    if not subnets:
        print("No Subnets found under the name tag " + data['name'])
    for subnet in subnets:
        _subnet_state[data['name']] = subnet

    return _subnet_state
