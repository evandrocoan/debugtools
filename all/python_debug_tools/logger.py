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

import timeit
import datetime

import logging
import platform

from logging import Logger
from logging import Manager

from logging import DEBUG
from logging import WARNING
from logging import _srcfile


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True


if hasattr(sys, '_getframe'):
    currentframe = lambda: sys._getframe(4)
else: #pragma: no cover
    def currentframe():
        """Return the frame object for the caller's stack frame."""
        try:
            raise Exception
        except Exception:
            return sys.exc_info()[3].tb_frame.f_back


class Debugger(Logger):
    """
        https://docs.python.org/2.6/library/logging.html
    """
    logger      = None
    output_file = None

    def __init__(self, debugger_name, logging_level=None, setup=False, **kwargs):
        """
            What is a clean, pythonic way to have multiple constructors in Python?
            https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python

            @param debugger_name the name of this logger accordingly with the standard logging.Logger() documentation.
            @param logging_level an integer with the current bitwise enabled log level
            @param setup whether or not to call now `setup()` with its **kwargs

            @param **kwargs are the parameters passed to the Debugger.setup() member function.
        """
        self.debugger_name = debugger_name
        super( Debugger, self ).__init__( self.debugger_name, logging_level or "DEBUG" )

        self.file_handler   = None
        self.stream_handler = None

        # Initialize the first last tick as the current tick
        self.lastTick = timeit.default_timer()

        # Enable debug messages: (bitwise)
        # 0 - Disabled debugging
        # 1 - Errors messages
        self.debug_level  = 127
        self._frameLevel  = 3
        self._debug_level = 0

        if setup:
            self.setup( **kwargs )

    def __call__(self, debug_level, msg, *args, **kwargs):
        """
            How to define global function in Python?
            https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python

            How to print list inside python print?
            https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
        """

        if self.debug_level & debug_level != 0:
            kwargs['debug_level'] = debug_level
            self._log( DEBUG, msg, args, **kwargs )

    def warn(self, msg, *args, **kwargs):
        """
            Fix second indirection created by the super().warn() method, by directly calling _log()
        """

        if self.isEnabledFor( WARNING ):
            self._log( WARNING, msg, args, **kwargs )

    def newline(self, level=1, count=1):
        """
            Prints a clean new line, without any formatter header.
        """
        self.clean( level, "" )

    def new_line(self, level=1, count=1):
        """
            Prints a clean new line, without any formatter header.
        """
        self.clean( level, "" )

    def clean(self, debug_level, msg, *args, **kwargs):
        """
            Prints a message without the time prefix as `[plugin_name.py] 11:13:51:0582059`

            How to insert newline in python logging?
            https://stackoverflow.com/questions/20111758/how-to-insert-newline-in-python-logging
        """

        if self.debug_level & debug_level != 0:
            self._debug_level = debug_level
            self.alternate( self.clean_formatter, debug_level, msg, *args, **kwargs )

    def basic(self, debug_level, msg, *args, **kwargs):
        """
            Prints the bitwise logging message with the standard basic formatter, which uses by
            default the format: [%(name)s] %(asctime)s:%(msecs)010.6f %(tickDifference).2e %(message)s

            The basic logger format can be configured setting the standard formatter with
            setup() and calling invert() to set the `full_formatter` as
            the basic formatter.
        """

        if self.debug_level & debug_level != 0:
            self.alternate( self.basic_formatter, debug_level, msg, *args, **kwargs )

    def alternate(self, formatter, debug_level, msg, *args, **kwargs):
        """
            Do a usual Debugger bitwise log using the specified logging.Formatter() object.
        """

        if self.debug_level & debug_level != 0:

            if self.stream_handler:
                self.stream_handler.setFormatter( formatter )

            if self.file_handler:
                self.file_handler.setFormatter( formatter )

            kwargs['debug_level'] = debug_level
            self._log( DEBUG, msg, args, **kwargs )

            if self.stream_handler:
                self.stream_handler.setFormatter( self.full_formatter )

            if self.file_handler:
                self.file_handler.setFormatter( self.full_formatter )

    def clear(self):
        """
            Clear the log file contents
        """

        if self.output_file:
            sys.stderr.write( "\n" + "Cleaning the file: " + self.output_file )
            open( self.output_file, 'w' ).close()

    def invert(self):
        """
            Inverts the default formatter between the preconfigured `basic` and `full_formatter`.
        """
        self.basic_formatter, self.full_formatter = self.full_formatter, self.basic_formatter

    def setup(self, file_path=None, mode='a', delete=True, date=False, level=False,
            function=True, name=True, time=True, tick=True, formatter=None):
        """
            Instead of output the debug to the standard output stream, send it a file on the file
            system, which is faster for large outputs.

            Single page cheat-sheet about Python string formatting pyformat.info
            https://github.com/ulope/pyformat.info

            Override a method at instance level
            https://stackoverflow.com/questions/394770/override-a-method-at-instance-level

            @param file_path    a relative or absolute path to the log file. If empty the output
                                will be sent to the standard output stream.

            @param mode         the file write mode on the file system. It can be `a` to append to
                                the existent file, or `w` to erase the existent file before start.

            @param delete       if True, it will delete all other handlers before activate the
                                current one, otherwise it will only activate the selected handler.

            @param date         if True, add to the `full_formatter` the date on the format `%Y-%m-%d`.
            @param level        if True, add to the `full_formatter` the log levels.
            @param function     if True, add to the `full_formatter` the function name.
            @param name         if True, add to the `full_formatter` the logger name.
            @param time         if True, add to the `full_formatter` the time on the format `%H:%M:%S:microseconds`.
            @param tick         if True, add to the `full_formatter` the time.perf_counter() difference from the last call.
            @param formatter    if not None, replace this `full_formatter` by the logging.Formatter() provided.
        """
        self._setup_full_formatter(date, level, function, name, time, tick, formatter)

        if file_path:
            self.output_file = self._get_debug_file_path( file_path )

            sys.stderr.write( "\n" + "".join( self._get_time_prefix( datetime.datetime.now() ) )
                    + "Logging to the file " + self.output_file + "\n" )

            if self.file_handler:
                self.removeHandler( self.file_handler )

            self.file_handler = logging.FileHandler( self.output_file, mode )
            self.file_handler.setFormatter( self.full_formatter )
            self.addHandler( self.file_handler )

            if delete \
                    and self.stream_handler:

                self.removeHandler( self.stream_handler )
                self.stream_handler.close()
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
                self.file_handler.close()
                self.file_handler = None

    def findCaller(self, stack_info=False):
        """
            Copied from the python 3.6.3 implementation, only changing the `sys._getframe(3)` to
            `sys._getframe(4)` because due the inheritance, we need to take a higher frame to get
            the correct function name, otherwise the result would always be `__call__`, which is the
            internal function we use here.

            Find the stack frame of the caller so that we can note the source file name, line number
            and function name.
        """
        f = currentframe()
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

    def getActiveLogger(self):
        """
            Works accordingly with super::hasHandlers(), except that this returns the activate
            logger object if it has some activate handler, or None if there are not loggers with
            active handlers.
        """
        current = self

        while current:

            if current.handlers:
                return current

            if not current.propagate:
                break

            else:
                current = current.parent

        return None

    def _log(self, level, msg, args, exc_info=None, extra={}, stack_info=False, debug_level=0):
        self.currentTick = timeit.default_timer()

        debug_level = "(%d)" % debug_level if debug_level else ""
        extra.update( {"debugLevel": debug_level, "tickDifference": self.currentTick - self.lastTick} )

        if is_python2:
            super( Debugger, self )._log( level, msg, args, exc_info, extra )

        else:
            super( Debugger, self )._log( level, msg, args, exc_info, extra, stack_info )

        self.lastTick = self.currentTick

    def _setup_full_formatter(self, date, level, function, name, time, tick, formatter):
        self.clean_formatter = logging.Formatter( "", "" )
        self.basic_formatter = logging.Formatter( "[%(name)s] %(asctime)s:%(msecs)010.6f "
                "%(tickDifference).2e %(message)s", "%H:%M:%S" )

        if formatter:
            self.full_formatter = formatter

        else:
            date_format = "%Y-%m-%d " if date else ""
            date_format += "%H:%M:%S" if time else ""

            if time:
                time = "%(asctime)s:%(msecs)010.6f " if len( date_format ) else ""

            else:
                time = "%(asctime)s" if len( date_format ) else ""

            name = "[%(name)s] "           if name else ""
            tick = "%(tickDifference).2e " if tick else ""

            level = "%(levelname)s%(debugLevel)s " if level else ""
            function = "%(funcName)s:%(lineno)d "  if function else ""

            self.full_formatter = logging.Formatter( "{}{}{}{}{}%(message)s".format( name, time, tick, level, function ),
                    date_format )

    def _get_time_prefix(self, currentTime):
        return [ "[%s]" % self.debugger_name,
                " %02d" % currentTime.hour,
                ":%02d" % currentTime.minute,
                ":%02d" % currentTime.second,
                ":%07d " % currentTime.microsecond ]

    @classmethod
    def _get_debug_file_path(cls, output_file):
        """
            Reliably detect Windows in Python
            https://stackoverflow.com/questions/1387222/reliably-detect-windows-in-python

            Convert "D:/User/Downloads/debug.txt"
            To "/cygwin/D/User/Downloads/debug.txt"
            To "/mnt/D/User/Downloads/debug.txt"
        """
        new_output    = output_file
        platform_info = platform.platform( True ).lower()

        if "cygwin" in platform_info:
            new_output = "/cygdrive/" + cls._remove_windows_driver_letter( output_file )

        elif "linux" in platform_info \
                and "microsoft" in platform_info:

            new_output = cls._remove_windows_driver_letter( output_file )
            new_output = "/mnt/" + new_output[0].lower() + new_output[1:]

        if os.path.isabs( new_output ):
            output_file = new_output

        else:
            output_file = output_file

        # print( "Debugger, _get_debug_file_path, output_file:   " + output_file )
        # print( "Debugger, _get_debug_file_path, isabs:         " + str( os.path.isabs( output_file ) ) )
        # print( "Debugger, _get_debug_file_path, platform_info: " + platform_info )
        return output_file

    @classmethod
    def _remove_windows_driver_letter(cls, output_file):
        output_file = output_file.replace( ":", "", 1 )
        output_file = output_file.replace( "\\", "/", 1 )
        return output_file.replace( "\\\\", "/", 1 )

    @classmethod
    def getRootLogger(cls):
        """
            Return the main root logger `root_debugger` used by this extension of the standard
            logging module.
        """
        return Debugger.root


# Setup the alternate debugger, completely independent of the standard logging module Logger class
root = Debugger( "root_debugger", "WARNING", False )
Debugger.root = root

Debugger.manager = Manager( root )
Debugger.manager.setLoggerClass( Debugger )


def getLogger(debug_level=127, debugger_name=None, **kwargs):
    """
    Return a logger with the specified name, creating it if necessary. If no name is specified,
    return a new logger based on the main logger file name.

    @param `debug_level` & `debugger_name` are the same parameters passed to the Debugger() constructor.
    @param `setup` if True, ensure there is at least one handler enabled in the hierarchy. If not,
        then the current created Logger will be called with `setup=True`. See also
        logging::Logger::getLogger()
    @param `**kwargs` are the parameters passed to the Debugger.setup() member function.
    """

    if debugger_name:

        if isinstance( debugger_name, int ):
            debug_level, debugger_name = debugger_name, debug_level

            if isinstance( debugger_name, int ):
                raise ValueError( "The variable `debugger_name` must be an instance of string, instead of `%s`." % str( debugger_name ) )

        else:

            if not isinstance( debug_level, int ):
                raise ValueError( "The variable `debugger_name` must be an instance of int, instead of `%s`." % debugger_name )

    else:

        if isinstance( debug_level, int ):
            debugger_name = os.path.basename( __file__ )

        else:
            debugger_name = debug_level
            debug_level   = 127

    logger = Debugger.manager.getLogger( debugger_name )
    logger.debug_level = debug_level

    if kwargs.pop( "setup", True ):
        active = logger.getActiveLogger()

        if not active:
            logger.setup( **kwargs )

    return logger

