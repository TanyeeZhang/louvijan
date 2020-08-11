# coding=utf-8
"""mail.py - This module provides classes for handling mail.
"""
import smtplib
import traceback
from email.header import Header
from email.mime.text import MIMEText

from louvijan.manager.config import Config
from louvijan.manager.base import PluginManager
import threading
from typing import List


class EMailManager(PluginManager):
    """This class is used to process email.
    """

    # This lock is used for sending mails.
    _lock = threading.Lock()

    def __init__(self, configManager: Config) -> None:
        super().__init__('email', configManager)
        self.__stmp = None

    def __send(self, message: str) -> None:
        """Send mail message.

        Args:
            message (str): Mail text string.

        Notes:
            See `SMTP` for details:
            https://docs.python.org/3/library/smtplib.html
            https://www.afternerd.com/blog/how-to-send-an-email-using-python-and-smtplib/
        """

        try:
            # acquire lock
            self.__class__._lock.acquire()
            self.__stmp = smtplib.SMTP()
            self.__stmp.connect(self.host, self.getattr('port'))
            self.__stmp.login(self.username, self.authcode)
            self.__stmp.sendmail(self.sender, self.get_receivers(self.receivers), message)
            self.__stmp.close()
        except smtplib.SMTPException as e:
            traceback.print_exc()
        finally:
            # release lock
            self.__class__._lock.release()

    def get_receivers(self, receivers: str) -> List[str]:
        """Get the list of receivers.

        Args:
            receivers (str): A comma-separated list in a configuration file

        Returns:
            list: The list of receivers.

        Examples:
            >>> EMailManager(None).get_receivers('one@example.com, two@example.com, three@example.com')
            ['one@example.com', 'two@example.com', 'three@example.com']
        """

        return list(map(lambda x: x.strip(), receivers.split(',')))

    def format_mail(self, message: str, subject: str = 'louvijan') -> str:
        """Converts a message string to a mail message.

        Args:
            message (str):  A message string.
            subject (str): The subject of email.

        Returns:
            str: Email message string.
        """

        message = MIMEText(message, 'plain', 'utf-8')
        message['From'] = Header(getattr(self, 'from', 'louvijan'), 'utf-8')
        message['To'] = Header(getattr(self, 'to', 'Ops'), 'utf-8')
        message['Subject'] = Header(getattr(self, 'subject', subject), 'utf-8')
        return message.as_string()

    def send(self, message, subject='louvijan'):
        """Send email method.
        """

        if self.enable and self.send_mail_flag in ['always', 'Always', 'ALWAYS',
                                                   'failure', 'Failure', 'FAILURE',
                                                   'success', 'Success', 'SUCCESS']:
            message = self.format_mail(message, subject)
            self.__send(message)
