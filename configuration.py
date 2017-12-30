""" Module to abstract and hide configuration. """

# encoding: UTF-8

from ConfigParser import SafeConfigParser
import lib.local_debug as local_debug

# read in configuration settings

CONFIG_FILE_NAME = "iReboot.config"

def get_config_file_location():
    """
    Get the location of the configuration file.

    >>> get_config_file_location()
    './'iReboot.config'
    """

    return './' + CONFIG_FILE_NAME


class Configuration(object):
    """
    Object to handle configuration of the iReboot.
    """

    def get_log_directory(self):
        """ returns the location of the logfile to use. """

        return self.__config_parser__.get('SETTINGS', 'LOGFILE_DIRECTORY')

    def __init__(self):
        print "SETTINGS" + get_config_file_location()

        self.__config_parser__ = SafeConfigParser()
        self.__config_parser__.read(get_config_file_location())
        self.log_filename = self.get_log_directory() + "iReboot.log"
        self.urls_to_check = self.__config_parser__.get(
            'SETTINGS', "URLS_TO_CHECK").split(',')
        self.relay_pin = self.__config_parser__.getint(
            'SETTINGS', 'RELAY_PIN')
        self.seconds_between_checks = self.__config_parser__.getint(
            'SETTINGS', 'SECONDS_BETWEEN_CHECKS')
        self.seconds_to_power_off = self.__config_parser__.getint(
            'SETTINGS', 'SECONDS_TO_POWER_OFF')
        self.seconds_to_wait_after_power_on = self.__config_parser__.getint(
            'SETTINGS', 'SECONDS_TO_WAIT_AFTER_POWER_ON')

        if local_debug.is_debug():
            self.utc_offset = 0
        else:
            self.utc_offset = self.__config_parser__.getint(
                'SETTINGS', 'UTC_OFFSET')

        try:
            self.test_mode = self.__config_parser__.getboolean(
                'SETTINGS', 'TEST_MODE')
        except:
            self.test_mode = False


##################
### UNIT TESTS ###
##################

def test_configuration():
    """ Test that the configuration is valid. """
    config = Configuration()

    assert config.relay_pin is not None
    assert config.relay_pin >= 1
    assert config.relay_pin < 32
    assert config.seconds_between_checks > 0
    assert config.seconds_to_power_off > 0
    assert config.seconds_to_wait_after_power_on > config.seconds_to_power_off


if __name__ == '__main__':
    import doctest

    print "Starting tests."

    doctest.testmod()

    print "Tests finished"
