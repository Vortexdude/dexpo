from dotenv import load_dotenv
import os


class Config:

    def __init__(self):
        load_dotenv(verbose=True)

    @staticmethod
    def _get_var(name: str | int | None, default) -> None:
        return os.getenv(name, default=default)

    @property
    def region(self) -> None:
        return self._get_var('region', "ap-south-1")

    @property
    def appname(self) -> None:
        return self._get_var("appname", "boto3-testing")

    @property
    def vpc_cidr(self) -> None:
        return self._get_var("vpc_cidr", "192.168.0.0/16")

    @property
    def vpc_name(self) -> None:
        return self._get_var("vpc_name", "boto3-testing-vpc")

    @property
    def vpc_id(self) -> None:
        return self._get_var("vpc_id", "vpc-08a62c4b70250463b")

    @property
    def route_table_name(self) -> None:
        return self._get_var("route_table_name", "boto3-testing-rt")

    @property
    def internet_gateway_name(self) -> None:
        return self._get_var("internet_gateway_name", "boto3-testing-ig")
