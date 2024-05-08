def run_module(action: str, data: dict):
    if action == 'validate':
        print("Validating")

    if action == 'apply':
        print("Applying")

    print(f"{data=}")