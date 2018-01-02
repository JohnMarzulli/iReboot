"""
Main entry code for iReboot
"""

# !python
#
#
# Author: John Marzulli
# https://github.com/JohnMarzulli/iReboot
# john.marzulli@gmail.com
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You can view the GNU General Public License at <http://www.gnu.org/licenses/>
#
# Written for Python 2.7
# You will need to:
# pip install isort
# pip install configparser
# pip install pytest
# pip install RPi.GPIO
#
# Includes provisions for the basic logic to be run
# for development\testing under Windows or Mac
#
# NOTE: To have this start automatically
#
# 1. sudo vim /etc/rc.local
# 2. Add the following line:
#    cd /home/pi/iReboot
# 3. (OPTIONAL) To have the device update its code automatically
#    when connected to wifi, add the following line
#    at the bottom of the file:
#    /bin/sh /home/pi/iReboot/update.sh
# 4. Add the following line at the bottom of the file:
#    NOTE: if this should be below the optional auto-update line
#    python /home/pi/iReboot/iReboot.py &

import logging
import logging.handlers
import configuration
from lib.logger import Logger
import command_processor


CONFIGURATION = configuration.Configuration()

LOG_LEVEL = logging.INFO

LOGGER = logging.getLogger("ireboot")
LOGGER.setLevel(LOG_LEVEL)
HANDLER = logging.handlers.RotatingFileHandler(
    CONFIGURATION.log_filename, maxBytes=1048576, backupCount=3)
HANDLER.setFormatter(logging.Formatter(
    '%(asctime)s %(levelname)-8s %(message)s'))
LOGGER.addHandler(HANDLER)

if __name__ == '__main__':
    while True:
        try:
            COMMAND_PROCESSOR = command_processor.CommandProcessor(
                CONFIGURATION, Logger(LOGGER))
            COMMAND_PROCESSOR.run()
        finally:
            pass
