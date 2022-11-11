from modules import utils


def _read_config_file(file):
    return utils.read_yml(f'configs/{file}.yml')


def _get_config(file, config_group_code_name, config_code_name):
    return _read_config_file(file)[config_group_code_name][config_code_name]
