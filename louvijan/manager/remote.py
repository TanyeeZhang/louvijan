# coding=utf-8
"""remote.py - This module provides classes for remote servers.
"""
import paramiko
from louvijan.manager.config import Config
from louvijan.manager.base import PluginManager
from louvijan.manager.log import LogManager


class RemoteManager(PluginManager):
    """This class is used to operate on a remote server.
    """

    def __init__(self, configManager: Config) -> None:
        super().__init__('remote', configManager)
        self.connected = False
        self.client = None

    def connect(self, log_manager: LogManager = None) -> None:
        """Connect to remote server.

        The main steps are as follows:
        1. Instantiate the class `SSHClient`;
        2. Call the method `connect` of the `SSHClient` class;
        3. If the connection fails, the exception information will be output in the log file;
        otherwise set `connected` to true, which means Successfully connected.
        """

        self.client = paramiko.SSHClient()

        # Automatically add a policy to save the host name and key information for the server.
        # If not added, hosts that are not recorded in the local know_hosts file will not be able to connect.
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        # Connect to SSH server to authenticate with username and password
        try:
            self.client.connect(hostname=self.ip, port=self.port, username=self.username,
                                password=self.password, timeout=5)
        except Exception:
            if log_manager and log_manager.enable:
                log_manager.logger.error('Timeout: Unable to connect the remote server with IP `{}`.'.format(self.ip))
        else:
            self.connected = True

    def exec_command(self, command: str, log_manager: LogManager = None) -> int:
        """execute commands on remote.

        Args:
            command (str): The command to run scripts.
            log_manager (LogManager): Class `LogManager` instance.

        Returns:
            int: The status code returned after executing the command.
        """

        stdin, stdout, stderr = self.client.exec_command(command)
        output_str = stdout.read().decode('utf-8')
        err_str = stderr.read().decode('utf-8').strip()
        _remote_out_format = 'Execute on the remote server with IP `{}`'
        _remote_err_format = 'Failed to execute on the remote server with IP `{}`\n{}'

        if log_manager and log_manager.enable:
            if output_str:
                log_manager.info(_remote_out_format.format(self.ip, output_str))
            if err_str:
                log_manager.error(_remote_err_format.format(self.ip, err_str))

        ret = 0 if err_str == '' else -1

        return ret
