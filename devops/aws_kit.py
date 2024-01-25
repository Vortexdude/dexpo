from config import Config

setting = Config()


class Setting:
    def __init__(self):
        self.vpc_name = setting.vpc_name
        self.region = setting.region
        self.vpc_id = setting.vpc_id
        self.vpc_cidr = setting.vpc_cidr
        self.appname = setting.appname
        self.route_table_name = setting.route_table_name
        self.internet_gateway_name = setting.internet_gateway_name
