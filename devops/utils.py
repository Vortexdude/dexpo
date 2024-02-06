import logging
import json
import pathlib
import argparse

class DexLogger:
    def __init__(self):
        FORMAT = '[%(levelname)s] - %(asctime)s - %(name)s - %(message)s'
        logging.basicConfig(
            filename="file.log",
            format=FORMAT,
            filemode="w"
        )

    def get_logger(self):
        return logging.getLogger("EC2")


class Utils:

    @staticmethod
    def read_json(file: str) -> dict:
        """
        Read the json file and return the json data 
        required the file name only it will resolve the path automatically

        """
        current_path = pathlib.Path().resolve()
        file = f"{current_path}/devops/{file}"
        with open(file) as JSON:
            json_dict = json.load(JSON)
        return json_dict


class Parser(argparse.ArgumentParser):
    def __init__(self):
        description = """
        Dexpo repository is used to create cloud infrastructure in AWS
        
        """
        epilog = """Print At the END"""
        super().__init__(
            description=description,
            epilog=epilog
        )
        self.add_all_arguments()

    def add_all_arguments(self):
        self.add_argument(
            'action',
            nargs="?",
            choices=["apply", "destroy"],
            help='Do some homework'
        )
        if not self.parse_args().action:
            return self.print_help()

    @property
    def args(self):
        return super().parse_args()
