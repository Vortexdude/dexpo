from dexpo.src.resources.main import Base, BaseAbstractmethod
from requests import get


class SecurityGroup(Base, BaseAbstractmethod):

    def __init__(self,
                 name: str = None,
                 deploy: str = False,
                 dry_run: bool = False,
                 description: str = "",
                 permissions: list = None):
        super().__init__(region='ap-south-1')
        self.name = name
        self.deploy = deploy
        self.dry_run = dry_run
        self.description = description
        self.permissions = permissions
        self.my_ip = get('https://api.ipify.org/').text

    def validate(self) -> list:
        sg_groups = []
        for ec2_security_group in self.client.describe_security_groups()['SecurityGroups']:
            if self.name == ec2_security_group['GroupName']:
                sg_groups.append(ec2_security_group)

        return sg_groups

    def create(self):
        pass

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def security_group_validator(data: dict) -> dict:
    _security_group_state = {}
    sg_obj = SecurityGroup(**data)
    security_groups = sg_obj.validate()
    if not security_groups:
        print("No Security Group found under the name tag " + data['name'])
    for security_group in security_groups:
        _security_group_state[data['name']] = security_group

    return _security_group_state
