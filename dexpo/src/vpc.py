from dexpo import Dexpo


class Vpc(Dexpo):
    """
    Example plugin class.
    """

    def example_method(self, *args, **kwargs):
        print("This is an example method from Plugin1.")


def create_vpc(data):
    print("Creating vpc...")


def vpc_validator(data):
    print(f"from validate function")
