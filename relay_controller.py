""" Module to control a Relay """

# encoding: UTF-8

import time
import Queue
from multiprocessing import Queue as MPQueue

import text
import lib.utilities as utilities
from lib.relay import PowerRelay


class RelayManager(object):
    """
    Class to command and control the power relay.
    """

    def turn_on(self):
        """
        Tells the relay to turn on.
        """

        if not self.is_relay_on():
            self.__relay_queue__.put(text.RELAY_ON_COMMAND)
            return True

        return False

    def turn_off(self):
        """
        Tells the relay to turn off.
        """
        if self.is_relay_on():
            self.__relay_queue__.put(text.RELAY_OFF_COMMAND)
            return True

        return False

    def is_relay_on(self):
        """
        Get the status of the relay.
        True is "ON"
        False is "OFF"
        """

        return self.__modem_relay__.get_io_pin_status() == 1

    def get_relay_time_remaining(self):
        """
        Returns a string saying how much time is left
        for the relay.
        """

        self.__logger__.log_info_message("get_relay_time_remaining()")

        time_remaining = ""

        if self.__relay_shutoff_timer__ is not None:
            self.__logger__.log_info_message("timer is not None")
            delta_time = self.__relay_shutoff_timer__ - time.time()
            self.__logger__.log_info_message("Got the delta")
            time_remaining = utilities.get_time_text(delta_time)
            self.__logger__.log_info_message("Got the text")
        else:
            self.__logger__.log_info_message("No time")
            time_remaining = "No time"

        self.__logger__.log_info_message("adding remaining")
        time_remaining += " left."

        self.__logger__.log_info_message("Done")

        return time_remaining

    def update(self):
        """
        Services the queue from the relay service thread.
        """

        self.__update_shutoff_timer__()

        # check the queue to deal with various issues,
        # such as Max relay time and the gas sensor being tripped
        while not self.__relay_queue__.empty():
            try:
                status_queue = self.__relay_queue__.get()

                if text.RELAY_ON_COMMAND in status_queue:
                    self.__start_relay_immediate__()

                if text.RELAY_OFF_COMMAND in status_queue:
                    self.__stop_relay_immediate__()

                if text.MAX_TIME in status_queue:
                    self.__max_time_immediate__()
            except Queue.Empty:
                pass

    def __init__(self,
                 configuration,
                 logger,
                 relay_on_callback,
                 relay_off_callback,
                 relay_max_time_callback):
        """ Initialize the object. """

        self.__configuration__ = configuration
        self.__logger__ = logger
        self.__on_callback__ = relay_on_callback
        self.__off_callback__ = relay_off_callback
        self.__max_time_callback__ = relay_max_time_callback

        # create relay relay instance
        self.__modem_relay__ = PowerRelay(
            "modem_relay", configuration.relay_pin)
        self.__relay_queue__ = MPQueue()

        # create queue to hold relay timer.
        self.__relay_shutoff_timer__ = None

        # make sure and turn relay off
        self.__modem_relay__.switch_low()

    def __max_time_immediate__(self):
        """
        Trigger everything associated with the timer
        being triggered.
        """
        if self.__max_time_callback__ is not None:
            self.__max_time_callback__()

        self.__stop_relay__()

    def __stop_relay_immediate__(self):
        """
        Turn off the relay.
        """
        if self.__off_callback__ is not None:
            self.__off_callback__()

        self.__stop_relay__()

    def __start_relay_immediate__(self):
        """
        Start the relay.
        """
        if self.__on_callback__ is not None:
            self.__on_callback__()

        self.__start_relay__()

    def __stop_relay__(self):
        """
        Stops the relay.
        """
        self.__logger__.log_info_message("__stop_relay__::switch_low()")
        self.__modem_relay__.switch_low()
        self.__logger__.log_info_message(
            "__stop_relay__::stop_relay_timer()")
        self.__stop_relay_timer__()

    def __start_relay__(self):
        """
        Starts the relay.
        """
        self.__logger__.log_info_message("__start_relay__::switch_high()")
        self.__modem_relay__.switch_high()
        self.__logger__.log_info_message(
            "__start_relay__::start_relay_timer()")
        self.__start_relay_timer__()

    def __stop_relay_timer__(self):
        """
        Stops the relay timer.
        """

        self.__logger__.log_info_message(
            "Cancelling the relay shutoff timer.")
        self.__relay_shutoff_timer__ = None

    def __start_relay_timer__(self):
        """
        Starts the shutdown timer for the relay.
        """
        self.__logger__.log_info_message("Starting the relay shutoff timer.")
        self.__relay_shutoff_timer__ = time.time() + self.__configuration__.seconds_to_power_off

        return True

    def __update_shutoff_timer__(self):
        """
        Check to see if the timer has expired.
        If so, then add it to the action.
        """

        if self.__relay_shutoff_timer__ is not None \
                and self.__relay_shutoff_timer__ < time.time():
            self.__relay_queue__.put(text.MAX_TIME)
        elif self.__relay_shutoff_timer__ is None \
                and self.is_relay_on():
            self.__logger__.log_warning_message(
                "Relay should not be on, but the PIN is still active... attempting shutdown.")
            self.__relay_queue__.put(text.RELAY_OFF_COMMAND)
