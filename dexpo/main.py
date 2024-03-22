# take the argument
# load the json
# pass with the pydantic
# load the module depending upon the validation
from dexpo.src.lib.parser import DexpoArgParser
from dexpo.src.lib.utils import load_json
from dexpo.src.lib.models import ConfigModel

if __name__ == "__main__":
    args = DexpoArgParser()
    config_file = args.config_file
    config_data = load_json(config_file)
    filtered_data = ConfigModel(**config_data)
    print(filtered_data)
    if args.apply:
        print("do something")
    if args.destroy:
        print("do not something")
