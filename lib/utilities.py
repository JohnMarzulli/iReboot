"""
Module to hold common utilities.
"""

import subprocess
from platform import system as system_name  # Returns the system/OS name

import local_debug


def ping(host_to_ping):
    """
    Returns True if host (str) responds to a ping request.
    Remember that some hosts may not respond to a ping request even if the host name is valid.

    >>> ping("www.google.com")
    True
    >>> ping("www.amazon.com")
    True
    >>> ping("www.bing.com")
    True
    >>> ping("t-his-isnt-a-site-python.com")
    False
    """

    # Ping parameters as function of OS
    # 32512 is command not found
    # on "darwin" ping is in /sbin/
    # on Raspbian, it is in /bin/
    path = "/bin/"
    os_name = system_name().lower()
    is_windows = os_name == "windows"
    is_mac = os_name == "darwin"

    if is_windows:
        path = ""
    elif is_mac:
        path = "/sbin/"
    ping_command = path + "ping"
    parameters = " "
    parameters += "-n" if is_windows else "-c"
    parameters += " 1 " + host_to_ping

    # Pinging
    command_result = 0
    ping_process = subprocess.Popen([ping_command + parameters],
                                    shell=True, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT)

    if ping_process is not None:
        ping_process.wait()
        command_result = ping_process.returncode
    else:
        print "Unable to get ping process!"

    return command_result == 0


def get_singular_or_plural(value, unit):
    """
    Returns the value with a singuar
    or plural form.
    """

    as_int = int(value)

    # Get rid of the decimal in
    # values like 1.0
    if as_int == value:
        value = as_int

    result = str(value) + " " + unit

    if value != 1:
        result += "s"

    return result


def get_time_text(number_of_seconds):
    """
    Returns the amount of time in the appropriate unit.
    >>> get_time_text(-1)
    'No time'
    >>> get_time_text(0)
    'No time'
    >>> get_time_text(1)
    '1 second'
    >>> get_time_text(30)
    '30 seconds'
    >>> get_time_text(59)
    '59 seconds'
    >>> get_time_text(60)
    '1 minute'
    >>> get_time_text(90)
    '1 minute'
    >>> get_time_text(120)
    '2 minutes'
    >>> get_time_text(600)
    '10 minutes'
    >>> get_time_text((60 * 60) - 1)
    '59 minutes'
    >>> get_time_text(60 * 60)
    '1 hour'
    >>> get_time_text((60 * 60) + 1)
    '1 hour'
    >>> get_time_text((60 * 60) * 1.5)
    '1.5 hours'
    >>> get_time_text((60 * 60) * 2)
    '2 hours'
    >>> get_time_text((60 * 60) * 23)
    '23 hours'
    >>> get_time_text((60 * 60) * 24)
    '1 day'
    >>> get_time_text((60 * 60) * 36)
    '1.5 days'
    >>> get_time_text((60 * 60) * 36.1234)
    '1.5 days'
    >>> get_time_text((60 * 60) * 48)
    '2 days'
    """

    if number_of_seconds <= 0:
        return "No time"

    if number_of_seconds < 60:
        return get_singular_or_plural(int(number_of_seconds), "second")

    number_of_minutes = number_of_seconds / 60

    if number_of_minutes < 60:
        return get_singular_or_plural(int(number_of_minutes), "minute")

    number_of_hours = round(number_of_minutes / 60.0, 1)

    if number_of_hours < 24:
        return get_singular_or_plural(number_of_hours, "hour")

    number_of_days = round(number_of_hours / 24.0, 1)

    return get_singular_or_plural(number_of_days, "day")


def escape(text):
    """
    Replaces escape sequences do they can be printed.

    Funny story. PyDoc can't unit test strings with a CR or LF...
    It gives a white space error.

    >>> escape("text")
    'text'
    >>> escape("")
    ''
    """

    return str(text).replace('\r', '\\r').replace('\n', '\\n').replace('\x1a', '\\x1a')


def get_cleaned_phone_number(dirty_number):
    """
    Removes any text from the phone number that
    could cause the command to not work.

    >>> get_cleaned_phone_number('"2061234567"')
    '2061234567'
    >>> get_cleaned_phone_number('+2061234567')
    '2061234567'
    >>> get_cleaned_phone_number('""+2061234567')
    '2061234567'
    >>> get_cleaned_phone_number('2061234567')
    '2061234567'
    >>> get_cleaned_phone_number('(206) 123-4567')
    '2061234567'
    >>> get_cleaned_phone_number(None)
    """
    if dirty_number is not None:
        return dirty_number.replace('+',
                                    '').replace('(',
                                                '').replace(')',
                                                            '').replace('-',
                                                                        '').replace(' ',
                                                                                    '').replace('"',
                                                                                                '')
    return None


def restart():
    """
    Restarts down the Pi.
    """

    if not local_debug.is_debug():
        subprocess.Popen(["sudo shutdown -r 30"],
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)


def shutdown():
    """
    Shuts down the Pi.
    """

    if not local_debug.is_debug():
        subprocess.Popen(["sudo shutdown -h 30"],
                         shell=True, stdout=subprocess.PIPE,
                         stderr=subprocess.STDOUT)


if __name__ == '__main__':
    import doctest

    print "Starting tests."

    doctest.testmod()

    print "Tests finished"
