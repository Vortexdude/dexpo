from dexpo.settings import args, initializer, CONF
from dexpo.src.resources import Controller


def main(action):
    controller = Controller(CONF)
    controller.validate()

    if action == 'apply':
        controller.apply()

    elif action == 'destroy':
        controller.destroy()


if __name__ == "__main__":
    initializer()
    _action = args.action
    main(_action)
