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

    def validate(self) -> dict:
        sg_groups = []
        for ec2_security_group in self.client.describe_security_groups()['SecurityGroups']:
            if self.name == ec2_security_group['GroupName']:
                sg_groups.append(ec2_security_group)
        if not sg_groups:
            return {}
        else:
            return sg_groups[0]

    def create(self, vpc_id):
        secGroup = self.resource.create_security_group(
            GroupName=self.name,
            Description="%s" % self.description,
            VpcId=vpc_id,
            TagSpecifications=[{
                "ResourceType": 'security-group',
                "Tags": [{
                    "Key": "Name",
                    "Value": self.name
                }]
            }]
        )

        if secGroup.id:
            secGroup.authorize_ingress(
                IpPermissions=self.permissions
            )
            print(f'Security Group {self.name} Created Successfully!')
            self.id = secGroup.id
            self._resource = self.resource.SecurityGroup(self.id)
        else:
            print('Error while creating ingress rule in the security Group')

        return secGroup.id

    def delete(self):
        pass

    def to_dict(self, prop: dict):
        pass


def security_group_validator(data: dict) -> dict:
    _security_group_state = {}
    sg_obj = SecurityGroup(**data)
    security_group = sg_obj.validate()
    if not security_group:
        print("No Security Group found under the name tag " + data['name'])
        return {}

    resource = sg_obj.resource.SecurityGroup(security_group['GroupId'])
    security_group.update({'resource': resource})
    return security_group


def create_security_group(data: dict, vpc_id) -> tuple:
    sg_object = SecurityGroup(**data)
    sg_id = sg_object.create(vpc_id)
    return sg_id, sg_object.resource.SecurityGroup(sg_id)
