#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

####################### Licensing #######################################################
#
# Debug Tools, Logging utilities
# Copyright (C) 2017 Evandro Coan <https://github.com/evandrocoan>
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
import sys

import time
import datetime

import logging
import platform

from logging import Logger
from logging import Manager

from logging import DEBUG
from logging import WARNING
from logging import _srcfile


class Debugger(Logger):
    """
        https://docs.python.org/2.6/library/logging.html
    """
    logger      = None
    output_file = None

    def __init__(self, debugger_name, logging_level=None):
        """
            What is a clean, pythonic way to have multiple constructors in Python?
            https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python
        """
        self.debugger_name = debugger_name
        super( Debugger, self ).__init__( self.debugger_name, logging_level or "DEBUG" )

        self.file_handler   = None
        self.stream_handler = None

        # Initialize the first last tick as the current tick
        self.lastTick = time.perf_counter()

        # Enable debug messages: (bitwise)
        # 0 - Disabled debugging
        # 1 - Errors messages
        self.debug_level  = 127
        self._debug_level = 0
        self.setup_logger()

    def __call__(self, debug_level, msg, *args, **kwargs):
        """
            How to define global function in Python?
            https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python

            How to print list inside python print?
            https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
        """

        if self.debug_level & debug_level != 0:
            self._log( DEBUG, msg, args, **kwargs )

    def insert_empty_line(self, level=1):
        self.clean( level, "" )

    def clean(self, debug_level, msg, *args, **kwargs):

        if self.debug_level & debug_level != 0:
            self._debug_level = debug_level
            self.alternate_formatter( self.clean_formatter, debug_level, msg, *args, **kwargs )

    def basic(self, debug_level, msg, *args, **kwargs):

        if self.debug_level & debug_level != 0:
            self.alternate_formatter( self.basic_formatter, debug_level, msg, *args, **kwargs )

    def alternate_formatter(self, formatter, debug_level, msg, *args, **kwargs):
        """
            Prints a message without the time prefix `[plugin_name.py] 11:13:51:0582059 `

            How to insert newline in python logging?
            https://stackoverflow.com/questions/20111758/how-to-insert-newline-in-python-logging
        """

        if self.debug_level & debug_level != 0:

            if self.stream_handler:
                self.stream_handler.setFormatter( formatter )

            if self.file_handler:
                self.file_handler.setFormatter( formatter )

            self._debug_level = debug_level
            self._log( DEBUG, msg, *args, **kwargs )

            if self.stream_handler:
                self.stream_handler.setFormatter( self.full_formatter )

            if self.file_handler:
                self.file_handler.setFormatter( self.full_formatter )

    def clear_log_file(self):
        """
            Clear the log file contents
        """

        if self.output_file:
            sys.stderr.write( "\n" + "Cleaning the file: " + self.output_file )
            open( self.output_file, 'w' ).close()

    def invert_basic_full_formatter(self):
        self.basic_formatter, self.full_formatter = self.full_formatter, self.basic_formatter

    def setup_logger(self, file_path=None, mode='a', delete=True, date=False, level=False):
        """
            Instead of output the debug to the standard output stream, send it a file on the file
            system, which is faster for large outputs.

            @param file_path    a relative or absolute path to the log file. If empty the output
                                will be sent to the standard output stream.

            @param mode         the file write mode on the file system. It can be `a` to append to
                                the existent file, or `w` to erase the existent file before start.

            @param delete       if True, it will delete all other handlers before activate the
                                current one, otherwise it will only activate the selected handler.

            @param date         if True, add to the `full_formatter` the date on the format `%Y-%m-%d`.
            @param level        if True, add to the `full_formatter` the current log levels.
        """

        # Single page cheat-sheet about Python string formatting pyformat.info
        # https://github.com/ulope/pyformat.info
        self.clean_formatter = logging.Formatter( "", "", style="{" )
        self.basic_formatter = logging.Formatter( "[{name}] {asctime}:{msecs:=010.6f} "
                "{tickDifference:.2e} {message}", "%H:%M:%S", style="{" )

        date = "%Y-%m-%d, " if date else ""
        level = "{levelname}({debugLevel}) " if level else ""

        self.full_formatter = logging.Formatter( "[{name}] {asctime}:{msecs:=010.6f} %s"
                "{tickDifference:.2e} {funcName}:{lineno} {message}" % ( level ),
                "{}%H:%M:%S".format( date ),
                style="{" )

        # Override a method at instance level
        # https://stackoverflow.com/questions/394770/override-a-method-at-instance-level
        if file_path:
            self.output_file = self._get_debug_file_path( file_path )
            sys.stderr.write( "\n" + self._get_time_prefix( datetime.datetime.now() ) + "Logging to the file " + self.output_file + "\n" )

            if self.file_handler:
                self.removeHandler( self.file_handler )

            self.file_handler = logging.FileHandler( self.output_file, mode )
            self.file_handler.setFormatter( self.full_formatter )
            self.addHandler( self.file_handler )

            if delete \
                    and self.stream_handler:

                self.removeHandler( self.stream_handler )
                self.stream_handler = None

        else:

            if self.stream_handler:
                self.stream_handler.setFormatter( self.full_formatter )

            else:
                self.stream_handler = logging.StreamHandler()
                self.stream_handler.setFormatter( self.full_formatter )
                self.addHandler( self.stream_handler )

                if delete \
                        and self.file_handler:

                    self.removeHandler( self.file_handler )
                    self.file_handler = None

    def findCaller(self, stack_info=False):
        """
            Copied from the python 3.6 implementation, only changing the `sys._getframe(1)` to
            `sys._getframe(3)` because due the inheritance, we need to take a higher frame to get
            the correct function name, otherwise the result would always be `__call__`, which is the
            internal function we use here.

            Find the stack frame of the caller so that we can note the source file name, line number
            and function name.
        """
        f = sys._getframe(3) if hasattr(sys, "_getframe") else None

        #On some versions of IronPython, currentframe() returns None if
        #IronPython isn't run with -X:Frames.
        if f is not None:
            f = f.f_back
        rv = "(unknown file)", 0, "(unknown function)", None
        while hasattr(f, "f_code"):
            co = f.f_code
            filename = os.path.normcase(co.co_filename)
            if filename == _srcfile:
                f = f.f_back
                continue
            sinfo = None
            if stack_info:
                sio = io.StringIO()
                sio.write('Stack (most recent call last):\n')
                traceback.print_stack(f, file=sio)
                sinfo = sio.getvalue()
                if sinfo[-1] == '\n':
                    sinfo = sinfo[:-1]
                sio.close()
            rv = (co.co_filename, f.f_lineno, co.co_name, sinfo)
            break
        return rv

    def warn(self, msg, *args, **kwargs):
        """
            Fix second indirection created by the super().warn() method, by directly calling _log()
        """

        if self.isEnabledFor(WARNING):
            self._log(WARNING, msg, args, **kwargs)

    def _log(self, level, msg, args, exc_info=None, extra={}, stack_info=False):
        self.currentTick = time.perf_counter()
        extra.update( {"debugLevel": self._debug_level, "tickDifference": self.currentTick - self.lastTick} )

        super( Debugger, self )._log( level, msg, args, exc_info, extra, stack_info )
        self.lastTick = self.currentTick

    def _get_time_prefix(self, currentTime):
        return [ "[%s]" % self.debugger_name,
                " %02d" % currentTime.hour,
                ":%02d" % currentTime.minute,
                ":%02d" % currentTime.second,
                ":%07d " % currentTime.microsecond ]

    def _get_debug_file_path(self, output_file):
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

            output_file = "/cygdrive/" + output_file

        else:
            output_file = output_file

        # print( "Debugger, _get_debug_file_path, PATH: " + output_file )
        return output_file


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

    logger.setup_logger( output_file )
    return logger

