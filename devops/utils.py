import logging
import json
import pathlib

FORMAT = '[%(levelname)s] - %(asctime)s - %(name)s - %(message)s'

logging.basicConfig(
    filename="file.log",
    format=FORMAT,
    filemode="w"
)

logger = logging.getLogger("EC2")
logger.setLevel(logging.INFO)



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
