
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
import platform
import os


class Debugger():

    startTime = datetime.datetime.now()
    lastTime  = startTime

    logger        = None
    output_file   = None
    debugger_name = os.path.basename( __file__ )

    def __init__(self, log_level=127, debugger_name=None, output_file=None):
        """
            What is a clean, pythonic way to have multiple constructors in Python?
            https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
        """
        # Enable debug messages: (bitwise)
        #
        # 0  - Disabled debugging.
        # 1  - Errors messages.
        self._log_level = log_level

        # Override a method at instance level
        # https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
        if output_file:
            self.setup_file_logger( output_file )
            self._log = self.create_file_logger()

        else:
            self._log = self.create_stream_logger()

        if debugger_name:
            self.debugger_name = debugger_name

    def __call__(self, log_level, *msg):
        currentTime = datetime.datetime.now()

        self._log( log_level, currentTime, msg )
        self.lastTime = currentTime

    def _log(self, log_level, currentTime, msg):
        raise NotImplementedError

    def setup_file_logger(self, output_file):
        self.__set_debug_file_path( output_file )
        print( "Logging the DebugTools debug to the file " + self.output_file )

        # Setup the logger
        logging.basicConfig( filename=self.output_file, format='%(asctime)s %(message)s', level=logging.DEBUG )

        # https://docs.python.org/2.6/library/logging.html
        self.logger = logging.getLogger( self.debugger_name )

    def create_file_logger(self):
        # How to define global function in Python?
        # https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
        def _log( log_level, currentTime, msg ):

            # You can access global variables without the global keyword.
            if self._log_level & log_level != 0:

                # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
                self.logger.debug( "[%s] " % self.debugger_name \
                        + str( currentTime.microsecond ) \
                        + "%7d " % ( currentTime.microsecond - self.lastTime.microsecond ) \
                        + "".join([str( m ) for m in msg]) )

        return _log

    def create_stream_logger(self):
        # How to define global function in Python?
        # https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
        def _log( log_level, currentTime, msg ):

            # You can access global variables without the global keyword.
            if self._log_level & log_level != 0:

                # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
                print( "[%s] " % self.debugger_name \
                        + "%02d" % currentTime.hour + ":" \
                        + "%02d" % currentTime.minute + ":" \
                        + "%02d" % currentTime.second + ":" \
                        + str( currentTime.microsecond ) \
                        + "%7d " % ( currentTime.microsecond - self.lastTime.microsecond ) \
                        + "".join([str( m ) for m in msg]) )

        return _log

    def clear_log_file(self):
        """
            Clear the log file contents
        """
        open(self.output_file, 'w').close()

    def __set_debug_file_path(self, output_file):
        """
            Reliably detect Windows in Python
            https://stackoverflow.com/questions/1387222/reliably-detect-windows-in-python
        """
        # Convert "D:/User/Downloads/debug.txt"
        # To "/cygwin/D/User/Downloads/debug.txt"
        if "CYGWIN" in platform.system().upper():
            output_file = output_file.replace( ":", "", 1 )
            output_file = output_file.replace( "\\", "/", 1 )
            output_file = output_file.replace( "\\\\", "/", 1 )

        self.output_file = "/cygdrive/" + output_file
        print( "PATH: " + self.output_file )


