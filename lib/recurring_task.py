"""
Module to handle tasks that occur on a regularly scheduled interval.
"""

import threading
import sys
import time

FUNCTION_A_COUNT = 0
FUNCTION_B_COUNT = 0

class RecurringTask(object):
    """
    Object to control and handle a recurring task.
    """

    def is_running(self):
        """
        Returns True if the task is running.
        """

        return self.__task_callback__ is not None and self.__is_running__

    def start(self):
        """
        Starts the task if it is not already running.
        """
        if self.__task_callback__ is not None and not self.__is_running__:
            self.__is_running__ = True
            self.__run_task__()

            return True

        return False

    def pause(self):
        """
        Pauses the task if it is running.
        """

        if self.is_running():
            self.__is_running__ = False

    def __run_task__(self):
        """
        Runs the callback.
        """

        if not self.__is_running__:
            return False

        try:
            self.__task_callback__()
        except:
            if self.__logger__ is not None:
                error_mesage = "EX(" + self.__task_name__ + ")=" + sys.exc_info()[0]
                self.__logger__.info(error_mesage)
        finally:
            if self.__is_running__:
                threading.Timer(int(self.__task_interval__), self.__run_task__).start()

    def __init__(self, task_name, task_interval, task_callback, logger=None, start_immediate=True):
        """
        Creates a new reocurring task.
        The call back is called at the given time schedule.
        """

        self.__task_name__ = task_name
        self.__task_interval__ = task_interval
        self.__task_callback__ = task_callback
        self.__logger__ = logger
        self.__is_running__ = False

        if start_immediate:
            self.start()
        else:
            threading.Timer(int(self.__task_interval__), self.__run_task__).start()

class timer_test(object):
    def __init__(self):
        self.a = 0
        self.b = 0

        RecurringTask("A", 1, self.increment_a)
        RecurringTask("B", 2, self.increment_b)

    def increment_a(self):
        self.a += 1

    def increment_b(self):
        self.b += 1

        if (self.b % 10) == 0:
            raise KeyboardInterrupt

if __name__ == '__main__':

    TEST = timer_test()

    while True:
        print "A:" + str(TEST.a)
        print "B:" + str(TEST.b)

        time.sleep(1)
