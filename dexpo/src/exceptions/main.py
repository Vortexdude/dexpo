class KeyMissingException(Exception):
    def __init__(self, key: str, module_name: str):
        super().__init__(f"{key} Key is missing for {module_name} in config")


class Boto3OperationError(Exception):
    def __init__(self):
        super().__init__("Cant able to Perform the operation")
