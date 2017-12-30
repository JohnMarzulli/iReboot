"""
Checks what the status of the internet is.
"""

import datetime
import lib.utilities as utilities
from lib.recurring_task import RecurringTask


class InternetStatus(object):
    """
    Class to check the status of the internet.
    """

    def is_internet_up(self):
        """
        Returns true if the internet is online.
        """

        return self.__is_internet_up__

    def __init__(self, configuration, logger):
        """
        Initializes the checker.
        """

        self.__logger__ = logger
        self.site_status = {}
        self.__urls_to_check__ = configuration.urls_to_check
        self.__is_internet_up__ = self.__can_the_internet_be_reached__()
        self.last_check_time = datetime.datetime.now()
        self.__status_task__ = RecurringTask("CheckInternet",
                                             configuration.seconds_between_checks,
                                             self.__check_internet_connectivity__,
                                             self.__logger__)

    def __can_the_internet_be_reached__(self):
        """
        Performs the check to see if the Internet is up.
        """

        self.last_check_time = datetime.datetime.now()

        # Nothing to check
        if self.__urls_to_check__ is None:
            return True

        num_sites = len(self.__urls_to_check__)

        if num_sites < 1:
            return True

        num_sites_up = 0
        self.site_status = {}

        try:
            for site in self.__urls_to_check__:
                contacted = utilities.ping(site)
                self.site_status[site] = contacted
                if contacted:
                    num_sites_up += 1

                if self.__logger__ is not None:
                    self.__logger__.log_info_message(
                        site + ":" + str(contacted))
        except:
            print "__can_the_internet_be_reached__:EXCEPTION"
            if self.__logger__ is not None:
                self.__logger__.log_warning_message(
                    "__can_the_internet_be_reached__:EXCEPTION")

        return num_sites_up > 0

    def __check_internet_connectivity__(self):
        """
        Update if the internet is up.
        """

        if self.__logger__ != None:
            self.__logger__.log_info_message("Updating Internet Status")

        self.__is_internet_up__ = self.__can_the_internet_be_reached__()

        if self.__logger__ != None:
            self.__logger__.log_info_message(
                "Internet: " + str(self.__is_internet_up__))


if __name__ == '__main__':
    from configuration import Configuration
    import time

    CONFIG = Configuration()
    STATUS_CHECKER = InternetStatus(CONFIG, None)

    if STATUS_CHECKER.is_internet_up():
        print "UP"
    else:
        print "DOWN"

    time.sleep(120)

    if STATUS_CHECKER.is_internet_up():
        print "UP"
    else:
        print "DOWN"
