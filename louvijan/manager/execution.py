# coding=utf-8
"""execution.py - This module provides classes that execute commands.
"""
import os
import sys
import signal
import subprocess
from .config import Config
from .base import PluginManager
from .log import LogManager


class ExecutionManager(PluginManager):
    """This class is used to execute commands for scripts running.
    """

    def __init__(self, configManager: Config) -> None:
        super().__init__('execution', configManager)
        self.force = getattr(self, 'force', True)
        self.executable = getattr(self, 'executable', str(sys.executable))

    def exec_command(self, command: str, log_manager: LogManager = None) -> int:
        """Execute the command and output to a log file or not.

        Args:
            command (str): Target command.
            log_manager (LogManager): Class `LogManager` instance.

        Returns:
            int：Status code returned by executing the command.
        """

        if log_manager:
            with open(log_manager.path, 'a') as log:
                # The child process calls the system command and prints the error message to a log file.
                ret = subprocess.call(command, shell=True, stdout=log, stderr=log)
                print(command)
                print('call', ret)
        else:
            ret = subprocess.call(command, shell=True)

        return ret

    def kill(self):
        """Force kill process to end execution.

        Notes:
            The kill operation on Linux system and Windows system may be different.
        """

        try:
            os.kill(os.getpid(), signal.SIGKILL)
        except:
            os.kill(os.getpid(), signal.CTRL_BREAK_EVENT)