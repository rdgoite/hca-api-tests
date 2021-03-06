from configparser import ConfigParser

import os

BASE_DIRECTORY = os.path.abspath(os.path.dirname(__file__))

_config = ConfigParser()
secret_file_path = os.path.join(BASE_DIRECTORY, 'secrets.ini')
_config.read(secret_file_path)


def get_default(secret):
    return _config.get('default', secret, fallback=None)