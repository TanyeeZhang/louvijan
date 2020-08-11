# coding=utf-8
"""config.py - This module provides operations on configuration files.
"""
import configparser
import os
import sys


class Config:
    """This class is used to manage configuration files.
    """

    def __new__(cls, *args, **kwargs):
        """Implementation of singleton class.
        """

        if not hasattr(cls, '_instance'):
            cls._instance = object.__new__(cls)
            # cls._cached = False
        return cls._instance

    def __init__(self, path: str = '') -> None:
        """Initialize the class.

        Args:
            path (str): The path to the configuration file.
            If null, the default configuration will be provided.
        """

        self.manager = configparser.ConfigParser()
        self.path = path
        if os.path.exists(self.path):
            self.manager.read(self.path, encoding='utf-8')
        else:
            self.init()

    def init(self):
        """Initialize the default configuration.
        """

        default_config_dict = {
            'execution': {
                'name': 'louvijan',
                'force': 'true',
                'executable': str(sys.executable)
            },
            'log': {
                'path': 'louvijan.log'
            },
            'email': {'host': 'smtp.qq.com', 'username': '676761828',
                      'port': '25', 'authcode': 'tbzdgadujpkdbfgc',
                      'sender': '676761828@qq.com', 'receivers': '676761828@qq.com',
                      'send_mail_flag': 'never'},
            # 'remote': {'ip': '10.10.10.10', 'port': '25'}
        }

        self.dict_to_config(default_config_dict)

    def dict_to_config(self, d: dict) -> None:
        """Turn the dictionary into a configuration file

        Args:
            d (dict) : Configuration of a dictionary.
        """

        for section in d.keys():
            self.manager.add_section(section)
            for option in d[section].keys():
                self.manager.set(section, option, d[section][option])

    def get_section(self, section: str) -> dict:
        """Get a dictionary for a specific section.

        Args:
            section: The section of `***.conf` file.

        Returns:
            dict: The configuration items as a dictionary.
        """

        return dict(self.manager.items(section))

    def template(self):
        """Write the configuration file to the template file `louvijan.conf.template` in the sibling directory.
        """

        template_dict = {
            'execution': {
                'name': 'louvijan',
                'force': 'true',
                'executable': 'python'
            },
            'log': {
                'path': 'louvijan.log', 'max_bytes': '10485760',
                'backupCount': '0',
                'formatter': '%(asctime)s - %(levelname)s - %(message)s',
                'level': 'INFO'
            },
            'email': {'host': 'xxxx.xx.com', 'username': 'xxxx',
                      'port': '25', 'authcode': '************',
                      'sender': '', 'receivers': '',
                      'send_mail_flag': 'always'},
            'remote': {'ip': '127.0.0.1', 'port': '22',
                       'username': 'root', 'password': '123456'}
        }

        self.manager = configparser.ConfigParser()
        self.dict_to_config(template_dict)
        with open('louvijan.conf.template', 'w') as f:
            self.manager.write(f)

    def __getattr__(self, item):
        return dict(self.manager.items(item))

    def __getitem__(self, index):
        return self.manager.sections()[index]

    def __str__(self):
        return str(self.manager)
