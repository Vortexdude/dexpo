from dexpo.settings import logger, args, initializer, CONF
from dexpo.src.controller.main import Controller


def main(action):
    controller = Controller(CONF)
    controller.validate()

    if action == 'apply':
        controller.apply()

    elif action == 'destroy':
        controller.destroy()


if __name__ == "__main__":
    logger.debug("Initializing project")
    initializer()
    _action = args.action
    logger.debug(f"Action {_action}")
    main(_action)
