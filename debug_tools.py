
####################### Licensing #######################################################
#
#   Copyright 2017 @ Evandro Coan
#
#   Originally written on:
#   https://github.com/evandrocoan/SublimeAMXX_Editor/blob/888c6822047d84e2370348b6cf5f4ac509f77b32/AMXXEditor.py#L1741-L1804
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or ( at
#  your option ) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################################
#


import datetime
import logging
import os

# convert to into a class member!
# https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
def _log(_log_level, log_level, currentTime, lastTime, debugger_name, msg, logger) :

    # You can access global variables without the global keyword.
    if _log_level & log_level != 0:

        # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
        print( "[%s] " % debugger_name \
                + "%02d" % currentTime.hour + ":" \
                + "%02d" % currentTime.minute + ":" \
                + "%02d" % currentTime.second + ":" \
                + str( currentTime.microsecond ) \
                + "%7d " % ( currentTime.microsecond - lastTime.microsecond ) \
                + "".join([str( m ) for m in msg]) )


class Debugger():

    # Enable debug messages: (bitwise)
    #
    # 0  - Disabled debugging.
    # 1  - Errors messages.
    _log_level   = 0

    startTime = datetime.datetime.now()
    lastTime  = startTime

    def __init__(self, log_level=1, debugger_name=None, output_file=None):
        """
        What is a clean, pythonic way to have multiple constructors in Python?
        https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
        """
        self._log_level  = log_level
        self.output_file = output_file

        if output_file:
            self.create_file_logger()

        else:
            self.logger = None

        if debugger_name:
            self.debugger_name = debugger_name

        else:
            self.debugger_name = os.path.basename( __file__ )

    def __call__(self, log_level, *msg):
        currentTime = datetime.datetime.now()

        _log( self._log_level, log_level, currentTime, self.lastTime, self.debugger_name, msg, self.logger )
        self.lastTime = currentTime

    def create_file_logger():

        # Clear the log file contents
        open(self.output_file, 'w').close()
        print( "Logging the DebugTools debug to the file " + self.output_file )

        # Setup the logger
        logging.basicConfig( filename=self.output_file, format='%(asctime)s %(message)s', level=logging.DEBUG )

        # https://docs.python.org/2.6/library/logging.html
        self.logger = logging.getLogger(self.debugger_name)

        # How to define global function in Python?
        # https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
        global _log

        def _log(_log_level, log_level, currentTime, lastTime, debugger_name, msg, logger):

            # You can access global variables without the global keyword.
            if _log_level & log_level != 0:

                # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
                logger.debug( "[%s] " % debugger_name \
                        + str( currentTime.microsecond ) \
                        + "%7d " % ( currentTime.microsecond - lastTime.microsecond ) \
                        + "".join([str( m ) for m in msg]) )


