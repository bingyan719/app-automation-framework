import os
import sys
import configparser

from .log import Logging
from . import constant


class Apps(object):
    def __init__(self):
        self.current_directory = os.path.split(os.path.realpath(sys.argv[0]))[0]
        self.project_directory = os.path.dirname(os.path.dirname(self.current_directory))
        self.path = self.project_directory + os.path.sep + 'configs' + os.path.sep + 'packages.conf'
        Logging.debug('packages path: {}'.format(self.path))
        if not os.path.exists(self.path):
            Logging.error('packages.conf is not exist, please check it.')
            exit(1)
        self.cf = configparser.ConfigParser()
        self.cf.read(self.path, encoding='utf-8')

    def get_section(self, section):
        """
        return all configurations under this parent_node
        """
        return self.cf[section]


class Settings(object):

    # TODO make this as singlton class
    def __init__(self):
        if constant.SETTINGS_CONFIG_PATH:
            #Logging.info('settings config file has specified, use it.')
            self.path = constant.SETTINGS_CONFIG_PATH
        else:
            #Logging.info('settings config file not specify, use default.')
            self.current_directory = os.path.split(os.path.realpath(sys.argv[0]))[0]
            #Logging.debug('current diectory: {}'.format(self.current_directory))
            self.project_directory = os.path.dirname(os.path.dirname(self.current_directory))
            #Logging.debug('current project directory: {}'.format(self.project_directory))
            self.path = self.project_directory + os.path.sep + 'configs' + os.path.sep + 'settings.conf'
        Logging.debug('settings path: {}'.format(self.path))
        if not os.path.exists(self.path):
            Logging.error('settings.conf is not exist, please check it.')
            exit(1)
        self.cf = configparser.ConfigParser()
        self.cf.read(self.path, encoding='utf-8')

    def get_ini(self, section, key):
        return self.cf.get(section, key)

    def set_ini(self, section, key, value):
        self.cf.set(section, key, value)
        return self.cf.write(open(self.path, "w", encoding='utf-8'))

    def add_ini(self, title):
        self.cf.add_section(title)
        return self.cf.write(open(self.path, encoding='utf-8'))

    def get_options(self, data):
        # 获取所有的section
        options = self.cf.options(data)
        return options

    def get_section(self, section):
        """
        return all configurations under this parent_node

        add by viking.den 2019.3.22
        """
        return self.cf[section]


class BlockoutsIni(object):

    def __init__(self, ini_path):
        self.ini_path = ini_path
        self.cf = configparser.ConfigParser()
        self.cf.read(self.ini_path, encoding='utf-8')

    def set_ini(self, section, key, value):
        self.cf.set(section, key, value)
        return self.cf.write(open(self.ini_path, "w", encoding='utf-8'))

    def add_ini(self, title):
        self.cf.add_section(title)
        return self.cf.write(open(self.ini_path, "w", encoding='utf-8'))

    
