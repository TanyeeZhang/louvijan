# coding=utf-8
"""base.py - Definition of base classes.
"""
from louvijan.manager.config import Config
from typing import Union


class PluginManager:
    """The base class of Manager, inherit it to extend the function of `Pipeline`.

    Its subclasses can be regarded as plugins, controlled by configuration files.
    """

    def __init__(self, name, configManager: Config) -> None:
        try:
            d = configManager.get_section(name)
        except:
            self.enable = False
            return
        else:
            self.enable = True
        for k, v in d.items():
            setattr(self, k, v)

    def getattr(self, option: str) -> Union[str, bool, int]:
        """Return options in the configuration file as a specific type.

        Args:
            option (str): options in the configuration file.

        Returns:
            str or bool or int: Type converted options.
        """

        res = getattr(self, option)
        if not isinstance(res, str):
            res = str(res)
        if res in ['True', 'true', 'TRUE', 'T', '0']:
            return True
        elif res in ['False', 'false', 'FALSE', 'F', '1']:
            return False
        elif res.isdigit():
            return int(res)
        return res




