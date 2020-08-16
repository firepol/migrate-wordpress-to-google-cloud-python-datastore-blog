import configparser
import os


def get_settings():
    settings = configparser.ConfigParser()
    base_path = os.path.dirname(os.path.realpath(__file__))  # make sure to return this path
    settings_ini_path = os.path.join(base_path, '../data/settings.ini')  # settings.ini relative path from here
    settings.read(settings_ini_path)
    return settings
