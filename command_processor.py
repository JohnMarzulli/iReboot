"""
Contains the response generated by a command request.
"""

import sys
import datetime
import socket
from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
from relay_controller import RelayManager
from internet_status import InternetStatus
from lib.recurring_task import RecurringTask
import lib.utilities as utilities
import lib.local_debug as local_debug
from lib.logger import Logger


class StatusServer(BaseHTTPRequestHandler):
    """
    Handles the HTTP response for status.
    """

    STATUS_HTML = "<html><body><h1>iReboot</h1></body></html>"

    def _set_headers(self):
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()

    def do_GET(self):
        """
        Returns normal webserver traffic.
        """

        self._set_headers()
        self.wfile.write(StatusServer.STATUS_HTML)

    def do_HEAD(self):
        self._set_headers()

    def do_POST(self):
        # Doesn't do anything with posted data
        self._set_headers()
        self.wfile.write("<html><body><h1>POST!</h1></body></html>")

# Main business logic of the iReboot
# Sets up up all of the connectivity checks
# Sets up the webserver
# Sets up the relay controller


class CommandProcessor(object):
    """
    Class to control a power relay based on internet connectivity.
    """

    ##############################
    #--- Public functions
    ##############################

    def run(self):
        """
        Service loop to run the iReboot
        """
        if self.__logger__ is not None:
            self.__logger__.log_info_message('Press Ctrl-C to quit.')

        # Serve forever never returns...
        RecurringTask("UpdateWebpage", 1, self.__update_webpage__,
                      self.__logger__, True)
        RecurringTask("ProcessConnectivity", self.__configuration__.seconds_between_checks,
                      self.__process_connectivity__, self.__logger__, True)
        RecurringTask("UpdateController", 1,
                      self.__relay_controller__.update, True)

        self.__httpd__.serve_forever()

    def __init__(self, buddy_configuration, logger):
        """
        Initialize the object.
        """

        self.__configuration__ = buddy_configuration
        self.__logger__ = logger
        self.__system_start_time__ = datetime.datetime.now()
        self.__modem_reboots__ = []

        # create heater relay instance
        self.__relay_controller__ = RelayManager(buddy_configuration, logger,
                                                 self.__relay_turned_on_callback__,
                                                 self.__relay_turned_off_callback__,
                                                 self.__relay_max_time_off_callback__)
        self.__internet_status__ = InternetStatus(
            self.__configuration__, self.__logger__)

        if logger is not None:
            self.__logger__.log_info_message(
                "Begin monitoring Internet status")

        port = 80
        local_ip = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(
            ('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]

        if local_debug.is_debug():
            local_ip = ''
            port = 8080

        server_address = (local_ip, port)
        self.__httpd__ = HTTPServer(server_address, StatusServer)

    def __last_modem_reboot__(self):
        """
        Returns when the last reboot was.
        """

        if self.__modem_reboots__ is None:
            return None

        num_entries = len(self.__modem_reboots__)

        if num_entries < 1:
            return None

        return self.__modem_reboots__[num_entries - 1]

    ##############################
    #-- Event callbacks
    ##############################

    def __relay_turned_on_callback__(self):
        """
        Callback that signals the relay turned the heater on.
        """

        if self.__logger__ is not None:
            self.__logger__.log_warning_message(
                "Starting reboot. Turning modem off.")

    def __relay_turned_off_callback__(self):
        """
        Callback that signals the relay turned the heater off.
        """

        if self.__logger__ is not None:
            self.__logger__.log_warning_message("Turning Modem on.")

    def __relay_max_time_off_callback__(self):
        """
        Callback that signals the relay turned the heater off due to the timer.
        """

        if self.__logger__ is not None:
            self.__logger__.log_warning_message(
                "Time limit reached, turning Modem back on.")

    ##############################
    #-- Command execution
    ##############################

    def __time_since_last_reboot__(self):
        """
        How long has it been since we last rebooted the modem?
        Returns the total uptime if the modem has not been rebooted
        since the process was started
        """

        if self.__last_modem_reboot__() is None:
            return (datetime.datetime.now() - self.__system_start_time__).total_seconds()

        return (datetime.datetime.now() - self.__last_modem_reboot__()).total_seconds()

    def __restart__(self):
        """
        Restarts the Pi
        """
        self.__logger__.log_info_message("RESTARTING. Turning off relay")
        self.__relay_controller__.turn_off()
        utilities.restart()

    def __shutdown__(self):
        """
        Shuts down the Pi
        """
        self.__logger__.log_info_message("SHUTDOWN: Turning off relay.")
        self.__relay_controller__.turn_off()

        self.__logger__.log_info_message(
            "SHUTDOWN: Shutting down iReboot.")
        utilities.shutdown()

    def __clear_queue__(self, queue):
        """
        Clears a given queue.
        """
        if queue is None:
            return False

        while not queue.empty():
            self.__logger__.log_info_message("cleared message from queue.")
            queue.get()

    ##############################
    #-- Recurring thread tasks
    ##############################

    def __get_local_time__(self, time_to_adjust):
        """
        Returns the local system time.
        """

        return time_to_adjust + datetime.timedelta(hours=self.__configuration__.utc_offset)

    def __update_webpage__(self):
        """
        Updates the webpage.
        """

        uptime = (datetime.datetime.now() -
                  self.__system_start_time__).total_seconds()

        new_html = "<html><body>\n"
        new_html += "<h1>iReboot</h1>\n"
        new_html += "<h2>Status</h2>\n"

        try:
            new_html += "<table>\n"
            new_html += "<tr><td>INTERNET</td><td><span style=\"background-color:"
            if self.__internet_status__.is_internet_up():
                new_html += "green;\">UP"
            else:
                new_html += "red;\">DOWN"
            new_html += "</span></td></tr>\n"
            new_html += "<tr><td>Modem</td><td><span style=\"background-color:"

            if self.__relay_controller__.is_relay_on():
                new_html += "yellow;\">SHUTDOWN"
            else:
                new_html += "green;\">POWERED"

            new_html += "</span></td></tr>\n"
            if self.__relay_controller__.is_relay_on():
                new_html += "<tr><td>REMAINING</td><td>" \
                            + self.__relay_controller__.get_relay_time_remaining() \
                            + "</td></tr>\n"

            new_html += "<tr><td>Last checked</td><td>" \
                            + str(self.__get_local_time__(self.__internet_status__.last_check_time)) \
                            + "</td></tr>\n"
            new_html += "<tr><td>Monitored</td><td>" + \
                utilities.get_time_text(uptime) + "</td></tr>\n"
            new_html += "</table><br>"

            new_html += "<h2>Sites</h2>\n"

            new_html += "<table>\n"
            new_html += "<tr><th>Site</th><th>Up</th></tr>\n"
            for site in self.__internet_status__.site_status:
                new_html += "<tr><td>" \
                            + site \
                            + "</td><td><span style=\"background-color:"
                if self.__internet_status__.site_status[site]:
                    new_html += "green;\">ONLINE"
                else:
                    new_html += "red;\">DOWN"

                new_html += "</span></td></tr>\n"
            new_html += "</table><br>\n"

            new_html += "<h2>Reboots</h2>\n"

            num_reboots = len(self.__modem_reboots__)
            if num_reboots == 0:
                new_html += "None<BR>"
            else:
                new_html += "<ul>"
                for reboot_time in reversed(self.__modem_reboots__):
                    new_html += "<li>"
                    new_html += str(self.__get_local_time__(reboot_time))
                    new_html += "</li>"
                new_html += "</ul><br>"

            new_html += "<p>Page generated at " + \
                str(datetime.datetime.now()) + "</p>"
        except:
            new_html += "<h2 style=\"background-color:red;\">ERROR generating page:</h2>\n"
            new_html += sys.exc_info()[0]
            new_html += "<br>"
        finally:
            new_html += "</body></html>"
            StatusServer.STATUS_HTML = new_html

            return new_html

    ##############################
    #-- Servicers
    ##############################

    def __process_connectivity__(self):
        """
        Process if we have connectivity to the internet.
        If we do not, then start the reboot process.
        Otherwise returns the number of total seconds.
        """

        should_start_reboot = False

        if not self.__internet_status__.is_internet_up():
            # Check to see if we are rebooting.
            time_since_last_reboot = self.__time_since_last_reboot__()
            next_reboot_time = self.__configuration__.seconds_to_wait_after_power_on \
                + self.__configuration__.seconds_to_power_off

            if time_since_last_reboot > next_reboot_time:
                should_start_reboot = True

        if should_start_reboot:
            self.__modem_reboots__.append(datetime.datetime.now())
            self.__relay_controller__.turn_on()

    def __run_servicer__(self, service_callback, service_name):
        """
        Calls and handles something with a servicer.
        """

        if service_callback is None:
            self.__logger__.log_warning_message(
                "Unable to service " + service_name)

        try:
            service_callback()
        except KeyboardInterrupt:
            print "Stopping due to CTRL+C"
            exit()
        except:
            self.__logger__.log_warning_message(
                "Exception while servicing " + service_name)
            print "Error:", sys.exc_info()[0]


##################
### UNIT TESTS ###
##################


#############
# SELF TEST #
#############
if __name__ == '__main__':
    import doctest
    import logging
    import configuration

    print "Starting tests."

    doctest.testmod()
    CONFIG = configuration.Configuration()

    CONTROLLER = CommandProcessor(
        CONFIG, Logger(logging.getLogger("Controller")))

    CONTROLLER.run()

    print "Tests finished"
    exit()
