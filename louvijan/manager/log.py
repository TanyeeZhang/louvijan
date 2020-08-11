# coding=utf-8
"""log.py - This module provides classes for logging.
"""
import logging
from logging.handlers import RotatingFileHandler
from .base import PluginManager
from .config import Config


class LogManager(PluginManager):
    """This class is responsible for managing log files.
    """

    def __init__(self, configManager: Config) -> None:
        super().__init__('log', configManager)

        # The default values
        max_bytes = 10485760  # 10MB
        backupCount = 0
        log_formatter = '%(asctime)s - %(levelname)s - %(message)s'
        level = 'INFO'
        self.logger = logging.getLogger(str(id(self)))
        self.logger.setLevel(level=logging.INFO)
        try:
            self.max_bytes = int(getattr(self, 'max_bytes', max_bytes))
        except Exception:
            raise ValueError('`max_bytes` must be an integer.')
        self.backupCount = int(getattr(self, 'backupCount', backupCount))
        self.log_formatter = getattr(self, 'formatter', log_formatter)
        self.level = getattr(logging, getattr(self, 'level', level))
        if hasattr(self, 'path'):
            self.__rotatingHandler = RotatingFileHandler(self.path, maxBytes=self.max_bytes, backupCount=1)
            self.__rotatingHandler.setLevel(self.level)
            self.__formatter = logging.Formatter(self.log_formatter)
            self.__rotatingHandler.setFormatter(self.__formatter)
            self.__console = logging.StreamHandler()
            self.__console.setLevel(logging.INFO)
            self.__console.setFormatter(self.__formatter)
            self.logger.addHandler(self.__rotatingHandler)
            self.logger.addHandler(self.__console)
