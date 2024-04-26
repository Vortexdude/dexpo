import os
import importlib

class Dexpo:
    """
    Main class for the plugin system.
    """
    def __init__(self):
        self.plugins = []

    def load_plugins(self, plugins_directory):
        """
        Load plugins from the specified directory.

        Parameters:
            plugins_directory (str): The directory containing plugin modules.
        """
        # Iterate over files in the plugins directory
        for file_name in os.listdir(plugins_directory):
            if file_name.endswith(".py") and file_name != "__init__.py":
                module_name = os.path.splitext(file_name)[0]
                module = importlib.import_module(f"dexpo.src.resources.vpc.{module_name}")
                for name in dir(module):
                    if f'create_{module_name.lower()}' in name:
                        create_object = getattr(module, name)
                        self.plugins.append(
                            {
                                module_name: {
                                    'create': create_object
                                }

                            }
                        )

                    if f'{module_name.lower()}_validator' in name:
                        validate_object = getattr(module, name)
                        self.plugins.append(
                            {
                                module_name: {
                                    'validate': validate_object
                                }
                            }
                        )

    def run_plugin_method(self, action, data, *args, **kwargs):
        """
        Run a method of all loaded plugins.
        here self.plugins is a list of dictionary that holds the key
        for deploy it should be deploy
        for validate it should be validate
        please do not use the more than one underscore(_)
             if you want to validate the internet gateway then you should create
             the function name -
             ig_validator(*args, **kwargs)
             create_ig(*args, **kwargs)
        Example:
             >>> plugin['vpc']['create'](data, *args)
             this will find the function name create_vpc(*args, **kwargs)
             >>> plugin['vpc']['validate'](data, *args)
             this iwll find the function name vpc_validator(*args, **kwargs)

        Parameters:
            action (str): The name of the method to run.
            *data: Positional arguments to pass to the method.
        """

        action, resource_name = action.split('_')
        for plugin in self.plugins:
            if resource_name in plugin:
                if action in plugin[resource_name]:
                    return plugin[resource_name][action](data, *args, **kwargs)
