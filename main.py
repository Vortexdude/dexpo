from devops.launcher import run
from devops.lib.utils import Parser

if __name__ == "__main__":
    dex_parser = Parser()
    action = dex_parser.args.action
    run(action)
