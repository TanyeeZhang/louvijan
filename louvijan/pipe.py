# coding=utf-8
"""pipe.py - The core module of `louvijan`.
"""
import time
import traceback
from concurrent.futures.thread import ThreadPoolExecutor
from concurrent.futures import as_completed
from queue import Queue
from louvijan.manager.config import Config
from louvijan.manager.log import LogManager
from louvijan.manager.remote import RemoteManager
from louvijan.manager.mail import EMailManager
from louvijan.manager.execution import ExecutionManager
from typing import List, Union, Tuple, Callable
from datetime import datetime


class PipeLine:
    """This class is the core class of `louvijan`, responsible for the definition and scheduling of all script tasks.
    """

    # The number of `Pipeline` objects.
    _count = 1
    # List of global error messages stored
    _errors = []
    # Record the start time of execution
    _time = time.time()

    def __init__(self, *args: Union[str, List, Callable], **kwargs):
        """Initialize each component.

        Args:
            args (str or list): Sequence and combination of commands.
            config='': The path to the configuration file,
            if null, the default configuration is provided.
        """

        config_path = kwargs.pop('config', '')

        self.config_manager = Config(config_path)
        self.execution_manager = ExecutionManager(self.config_manager)
        self.log_manager = LogManager(self.config_manager)
        self.remote_manager = RemoteManager(self.config_manager)
        self.email_manager = EMailManager(self.config_manager)

        # When an error is encountered, whether to FORCE the operation to continue
        # If true, it means that whether there is an exception or an error, it will be executed to the end.
        self.force = self.execution_manager.getattr('force')
        # The name of execution that can be configured in the `*.conf` file.
        self.name = getattr(self.execution_manager, 'name', 'louvijan')
        # List of of instance error messages stored
        self.errors = []
        # Startup time of instance
        self.start = time.time()
        # The queue that stores tasks
        self.__queue = Queue()
        # Parallel tasks are executed by thread pool
        self.__executor = ThreadPoolExecutor()
        self.__logger = self.log_manager.logger if self.log_manager.enable else None
        # The executable command to execute (Python) scripts
        self.__executable = self.execution_manager.executable
        # Resolves the script names to commands
        for arg in args:
            self.__cmd = ''
            if isinstance(arg, self.__class__):
                self.__class__._count += 1
                self.__queue.put(arg)
            elif isinstance(arg, list):
                self.__cmd = self.__flatten(arg)
            elif isinstance(arg, str):
                name = arg.strip()
                if name:
                    self.__cmd = '{} {}'.format(self.__executable, name)
                else:
                    raise ValueError("Filename or command can't be None.")
            else:
                raise TypeError('Error input type for filename or command.')
            self.__cmd != '' and self.__queue.put(self.__cmd)

        if self.remote_manager.enable:
            self.remote_manager.connect(self.log_manager)

    def __call__(self, *args, **kwargs):
        self.dispatch()

    def __rshift__(self, other):
        pass

    def __flatten(self, input_arr: List[Union[str, List]]) -> List[Union[str, List]]:
        """Flatten out the nested structure of the script list.

        Args:
            input_arr (list): List of script tasks.

        Returns:
            list: Flattened list.

        Notes:
            Multiple levels of nesting in a parallel list will be considered parallel at the same level.
            e.g.
            ['A', ['B', ['C', 'D'], 'E'], 'F'] => ['A', ['B', 'C', 'D', 'E'], 'F']
            Or
            ['A', ['B', [PipeLine(['C', 'D']), 'E']], 'F'] => ['A', ['B', PipeLine(['C', 'D']), 'E'], 'F']
        """

        tmp_output_arr = []
        output_arr = []
        while True:
            if not input_arr:
                break
            for index, i in enumerate(input_arr):
                if isinstance(i, list):
                    input_arr = i + input_arr[index + 1:]
                    break
                else:
                    if i != '':
                        tmp_output_arr.append(i)
                        if isinstance(i, self.__class__):
                            self.__class__._count += 1
                    input_arr.pop(index)
                    break

        # Concatenates the executable command with the script name
        for item in tmp_output_arr:
            if isinstance(item, str):
                output_arr.append('{} {}'.format(self.__executable, str(item)))
            else:
                output_arr.append(item)

        return output_arr

    def __do_task(self, cmd):
        self.__exec_cmd(cmd)

    def __exec_cmd(self, command: Union[str, Tuple, Callable]) -> None:
        """Execute the command.

        Args:
            command (str, tuple, class): Specific script commands.

        Notes:
            The overview of the method is:
            When the incoming parameter is a string, the remote server or local server is called to execute the script;
            if it is a `PipeLine` class object, it will be scheduled.
        """
        # The parameters passed in the submit method of ThreadPoolExecutor can be tuples
        if isinstance(command, tuple):
            command = command[0]
        if isinstance(command, self.__class__):
            command.dispatch()
        if isinstance(command, str):
            ret = -1
            try:
                start = time.time()
                if self.remote_manager.connected:
                    if self.log_manager.enable:
                        self.remote_manager.exec_command(command, self.log_manager)
                else:
                    if self.log_manager.enable:
                        ret = self.execution_manager.exec_command(command, self.log_manager)
                    else:
                        ret = self.execution_manager.exec_command(command)

                end = time.time()

                if ret == 0:
                    # Calculate the elapsed time for the script to run
                    cost = end - start
                    self.__logger and self.__logger.info('{}\nRun successfully and cost {} seconds.\n'.format(command, cost))
                else:
                    err = '{}\nRun Failed.\n'.format(command)
                    self.__logger.error(err)
                    self.__class__._errors.append((ret, err))
                    self.errors.append((ret, err))
                    # If no enforcement is set, the message is sent and the program is forcibly terminated
                    if not self.force:
                        self.email_manager.send(err)
                        self.execution_manager.kill()
            except Exception as e:
                traceback.print_exc()
        else:
            raise TypeError('Command Type error: it must be `str` or `PipeLine` or `tuple`.')

    def dispatch(self) -> None:
        """Dispatch and schedule parallel tasks.

        Suppose we have multiple tasks that need to be executed in a certain order, the flowchart is as follows:

              ->  B      -> E
        A ->  ->  C  ->        -> G
              ->  D      -> F


        e.g. PipeLine('A.py', ['B.py', 'C.py', 'D.py'], ['E.py', 'F.py'], 'G.py')

        e.g. PipeLine('A.py', PipeLine(['B.py', 'C.py', 'D.py'], config='xxx.conf'),
             PipeLine(['E.py', 'F.py'], config='yyy.conf'), 'G.py')


        The main steps of the method are as follows:

        1. Pop items from queue in turn util it is empty;
        2. If the type of item is `str`, execute it directly;
           in case of `Pipeline`, call the `dispatch` method to execute recursively;
           for `list`, submit the task to the thread pool and wait for it to complete.
        """

        self.start = time.time()
        while not self.__queue.empty():
            item = self.__queue.get()
            ret = -1
            if isinstance(item, str):
                self.__exec_cmd(item)
            if isinstance(item, self.__class__):
                # Recursively dispatch
                item.dispatch()
            # `list` represents parallel execution
            elif isinstance(item, list):
                # Commit the task to the thread pool
                tasks = [self.__executor.submit(self.__do_task, i) for i in item]
                # Wait for the tasks to complete
                for task in as_completed(tasks):
                    try:
                        # whether it is complete, return True/False
                        ret = task.done()
                        if ret:
                            continue
                    except Exception as e:
                        task.cancel()
                        traceback.print_exc()

    def __format_msg(self, g=True) -> str:
        """Format the output information at the end of the execution.

        Args:
            g (bool):  If True, global information; otherwise, instance information.

        Returns:
            str: The information to output.
        """

        obj = self.__class__ if g else self
        error_attr = '_errors' if g else 'errors'
        start_time_attr = '_time' if g else 'start'
        if not hasattr(obj, error_attr):
            raise AttributeError('`{}` has no attribute `{}`.'.format(type(obj), error_attr))
        # if there is any mistake during execution
        if not len(getattr(obj, error_attr)):
            msg = 'Execution succeeded in {}.'.format(self.name) if self.name else 'Execution succeeded.'
            if hasattr(obj, start_time_attr):
                _cost = '\nThis Task costs {} seconds in total.'.format(
                    str(round(time.time() - getattr(obj, start_time_attr), 2)))
            else:
                _cost = ''
            msg += _cost
            self.__logger and self.__logger.info(msg)
        else:
            msg_arr = []
            for i, item in getattr(obj, error_attr):
                msg_arr.append(item)
            msg = ''.join(msg_arr)
        return msg

    def __del__(self):
        """This destructor's job is to deal with the aftereffects.

        Notes:
            After the commands have been executed, some things need to be processed,
        such as writing logs, calculating elapsed time, and sending emails etc.
        """

        if self.remote_manager.connected:
            self.remote_manager.client.close()
        cls = self.__class__
        cls._count -= 1
        # When the last `PipeLine` object is released
        if cls._count == 0:
            self.email_manager.send(self.__format_msg())
        else:
            msg = self.__format_msg(g=False)
            self.email_manager.send(msg)
