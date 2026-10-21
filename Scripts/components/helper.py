"""
Module to include helper methods
"""

import os
from configparser import ConfigParser


def get_config_variable(env_var: str, config_path: list, config: ConfigParser, required: bool = False) -> str | None:
    """
    Parses the configuration option.
    Reads the configuration first from the environemnt else from the config file

    ## Parameters

    env_var (str): environment variable for the config option

    config_path (list): path of the config option in the config dict

    config (ConfigParser): ConfigParser object consisting of all the config

    required (bool): Indicates if the config option is required

    ## Returns

    The config value as a `str`
    """

    if os.getenv(env_var) is not None:
        result = os.getenv(env_var)
    elif config_path[0] in config and config_path[1] in config[config_path[0]]:
        result = config[config_path[0]][config_path[1]]
    else:
        result = None

    if all([required, result is None]):
        raise ValueError(f"The configuration option {env_var} is required")

    return result
