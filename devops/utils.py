import logging
import json
import pathlib


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
