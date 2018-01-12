#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2017 @ Evandro Coan
#   Simple debugger
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

import os

import time
import datetime

import logging
import platform

from logging import Logger
from logging import Manager


class Debugger(Logger):

    logger      = None
    output_file = None

    def __init__(self, debugger_name, logging_level=None):
        """
            What is a clean, pythonic way to have multiple constructors in Python?
            https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
        """
        self.debugger_name = debugger_name
        super( Debugger, self ).__init__( self.debugger_name, logging_level or "DEBUG" )

        # Initialize the first last tick as the current tick
        self.lastTick = time.perf_counter()

        # Enable debug messages: (bitwise)
        # 0 - Disabled debugging
        # 1 - Errors messages
        self.debug_level = 127
        self.set_file_logger( None )

    def __call__(self, debug_level, *msg):
        self.currentTick = time.perf_counter()

        self._log( debug_level, msg )
        self.lastTick = self.currentTick

    def clear_log_file(self):
        """
            Clear the log file contents
        """

        if self.output_file:
            print( "Cleaning the file: " + self.output_file )

            # os.remove(self.output_file)
            open(self.output_file, 'w').close()

    def set_file_logger(self, output_file=None):
        """
            Instead of output the debug to the standard output stream, send it a file on the file
            system, which is faster for large outputs.

            @param output_file   a relative or absolute path to the log file. If empty the output
            will be sent to the standard output stream.
        """

        # Override a method at instance level
        # https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
        if output_file:
            self._is_logging_file = True

            self._setup_file_logger( output_file )
            self._log = self._create_file_logger()

        else:
            self._is_logging_file = False
            self._log = self._create_stream_logger()

    def clean(self, debug_level, output):
        """
            Prints a message without the time prefix `[plugin_name.py] 11:13:51:0582059 `
        """

        if self.debug_level & debug_level != 0:
            message = "".join( [ str( m ) for m in output ] )

            if self._is_logging_file:
                self.logger.debug( message )

            else:
                print( message )

    def insert_empty_line(self, level=1):
        self.clean( level, "" )

    def _log(self, debug_level, msg):
        raise NotImplementedError

    def _setup_file_logger(self, output_file):
        self._set_debug_file_path( output_file )

        print( "" )
        print( self._get_time_prefix( datetime.datetime.now() ) + "Logging the DebugTools debug to the file " + self.output_file )

        # Setup the logger
        logging.basicConfig( filename=self.output_file, format='%(asctime)s %(message)s', level=logging.DEBUG )

        # https://docs.python.org/2.6/library/logging.html
        self.logger = logging.getLogger( self.debugger_name )

    def _create_file_logger(self):

        # How to define global function in Python?
        # https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
        def log( debug_level, msg ):

            if self.debug_level & debug_level != 0:

                # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
                self.logger.debug( "".join(
                        [
                            "[%s] " % self.debugger_name,
                            "%7d "  % datetime.datetime.now().microsecond,
                            "%7d "  % self._deltatime_difference()
                        ]
                        + [ str( m ) for m in msg ] ) )

        return log

    def _create_stream_logger(self):

        # How to define global function in Python?
        # https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python
        def log( debug_level, msg ):

            if self.debug_level & debug_level != 0:

                # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
                print( "".join(
                        self._get_time_prefix( datetime.datetime.now() )
                        + [ "%.2e " % self._deltatime_difference() ]
                        + [ str( m ) for m in msg ] ) )

        return log

    def _deltatime_difference(self):
        return self.currentTick - self.lastTick

    def _get_time_prefix(self, currentTime):
        return [ "[%s]" % self.debugger_name,
                " %02d" % currentTime.hour,
                ":%02d" % currentTime.minute,
                ":%02d" % currentTime.second,
                ":%07d " % currentTime.microsecond ]

    def _set_debug_file_path(self, output_file):
        """
            Reliably detect Windows in Python
            https://stackoverflow.com/questions/1387222/reliably-detect-windows-in-python

            Convert "D:/User/Downloads/debug.txt"
            To "/cygwin/D/User/Downloads/debug.txt"
        """

        if "CYGWIN" in platform.system().upper() and os.path.isabs( output_file ):
            output_file = output_file.replace( ":", "", 1 )
            output_file = output_file.replace( "\\", "/", 1 )
            output_file = output_file.replace( "\\\\", "/", 1 )

            self.output_file = "/cygdrive/" + output_file

        else:
            self.output_file = output_file

        # print( "PATH: " + self.output_file )


# Setup the alternate debugger
Debugger.manager = Manager( Logger.root )
Debugger.manager.loggerClass = Debugger


def getLogger(debug_level=127, debugger_name=None, output_file=None):
    """
    Return a logger with the specified name, creating it if necessary.

    If no name is specified, return a new logger based on the main logger file name.
    """
    logger = Debugger.manager.getLogger( debugger_name if debugger_name else os.path.basename( __file__ ) )
    logger.debug_level = debug_level

    logger.set_file_logger( output_file )
    return logger

