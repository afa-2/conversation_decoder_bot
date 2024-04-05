import os
import json


def get_settings():
    """
    Получает настройки из конфигурационного файла.
    :return: Возвращает словарь с настройками.
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    config_file = os.path.join(script_dir, '..', 'config_files_and_secret_inf', 'config.json')

    with open(config_file) as config_file:
        config = json.load(config_file)

    return config

