import os
import pathlib
import filecmp

project_home_path = pathlib.Path(__file__).parent.resolve()
project_name = os.path.basename(project_home_path)

state_file_path = os.path.join(project_home_path, 'devops', 'state')
config_file_path = os.path.join(project_home_path, 'devops', 'env')
_f1 = os.path.join(config_file_path, 'config.json')
_f2 = os.path.join(state_file_path, 'state.json')

