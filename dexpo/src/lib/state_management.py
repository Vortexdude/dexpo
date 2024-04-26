class ResourceManager:
    def __init__(self):
        self.data = {}

    @staticmethod
    def formatter(name, _id, resource):
        return {name: {"id": _id, 'resource': resource}}


state = ResourceManager()
