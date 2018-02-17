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
import platform

import logging
import logging.handlers

from logging import Logger
from logging import Manager
from logging import PlaceHolder

from logging import DEBUG
from logging import WARNING
from logging import CRITICAL

from logging import NOTSET
from logging import _srcfile

from concurrent_log_handler import ConcurrentRotatingFileHandler


is_python2 = False
EMPTY_KWARG = -sys.maxsize

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

        How to define global function in Python?
        https://stackoverflow.com/questions/27930038/how-to-define-global-function-in-python

        How to print list inside python print?
        https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
    """
    logger      = None
    output_file = None

    def __init__(self, logger_name, logger_level=None):
        """
            What is a clean, pythonic way to have multiple constructors in Python?
            https://stackoverflow.com/questions/682504/what-is-a-clean-pythonic-way-to-have-multiple-constructors-in-python

            @param `logger_name` the name of this logger accordingly with the standard logging.Logger() documentation.
            @param `logger_level` an integer with the current bitwise enabled log level
        """
        self.reset()
        super( Debugger, self ).__init__( logger_name, logger_level or "DEBUG" )

        self.file_handler   = None
        self.stream_handler = None

        # Initialize the first last tick as the current tick
        self.lastTick = timeit.default_timer()
        self._setup_formatters( self, self.default_arguments )

        # Enable debug messages: (bitwise)
        # 0 - Disabled debugging
        # 1 - Errors messages
        self._frameLevel  = 3
        self._debug_level = 127

    @property
    def debug_level(self):
        return self.debug_level

    @debug_level.setter
    def debug_level(self, debug_level):

        if isinstance( debug_level, int ):
            self._debug_level = debug_level

        else:
            raise ValueError( "Error: The debug_level `%s` must be an integer!" % debug_level )

    def __str__(self):
        total_loggers = 0
        representations = []
        loggers = Debugger.manager.loggerDict

        for logger_name in loggers:
            logger = loggers[logger_name]
            total_loggers += 1
            current_logger = "True_" if logger == self else "False"

            if isinstance( logger, PlaceHolder ):
                representations.append( "%2d. PlaceHolder(%s), %s" %
                        ( total_loggers, current_logger,
                        "".join( ["loggerMap(%s): %s" % (item.name, logger.loggerMap[item])
                                                       for item in logger.loggerMap] ) ) )

            else:
                representations.append( "%2d. name(%s): %-30s, _debug_level: %3d, propagate: %5s, "
                    "_frameLevel: %2d, stream_handler: %s, file_handler: %s, default_arguments: %s" %
                    ( total_loggers, current_logger, logger.name, logger._debug_level,
                    logger.propagate, logger._frameLevel, logger.stream_handler, logger.file_handler,
                    logger.default_arguments ) )

        return "\n%s" % "\n".join( reversed( representations ) )

    def __call__(self, debug_level, msg, *args, **kwargs):
        """
            Log to the current active handlers its message based on the bitwise `self._debug_level`
            value. Note, differently from the standard logging level, each logger object has its own
            bitwise logging level, instead of all sharing the main `level`.
        """

        if self._debug_level & debug_level != 0:
            kwargs['debug_level'] = debug_level
            self._log( DEBUG, msg, args, **kwargs )

    def reset(self):
        """
            Used to remember the these parameters values set on the subsequent calls to `setup()`.
            Call this if you want to reset to default all the parameters values. Note, you still
            need to call Debugger::setup() to this changes take effect.
        """
        self.default_arguments = \
        {
            "file": None,
            "mode": 'a',
            "delete": True,
            "date": False,
            "level": False,
            "function": not is_python2,
            "name": True,
            "time": True,
            "tick": True,
            "formatter": None,
            "rotation": 0,
            "msecs": True,
        }

    def active(self):
        """
            Works accordingly with super::hasHandlers(), except that this returns the activate
            logger object if it has some activate handler, or None if there are not loggers with
            active handlers.

            The root logger is not returned, unless it is already setup with handlers.
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

        if self._debug_level & debug_level != 0:
            self.alternate( self.clean_formatter, debug_level, msg, *args, **kwargs )

    def basic(self, debug_level, msg, *args, **kwargs):
        """
            Prints the bitwise logging message with the standard basic formatter, which uses by
            default the format: [%(name)s] %(asctime)s:%(msecs)010.6f %(tickDifference).2e %(message)s

            The basic logger format can be configured setting the standard formatter with
            setup() and calling invert() to set the `full_formatter` as
            the basic formatter.
        """

        if self._debug_level & debug_level != 0:
            self.alternate( self.basic_formatter, debug_level, msg, *args, **kwargs )

    def alternate(self, formatter, debug_level, msg, *args, **kwargs):
        """
            Do a usual Debugger bitwise log using the specified logging.Formatter() object.
        """

        if self._debug_level & debug_level != 0:

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
            sys.stderr.write( "Cleaning the file: " + self.output_file + "\n" )
            open( self.output_file, 'w' ).close()

    def invert(self):
        """
            Inverts the default formatter between the preconfigured `basic` and `full_formatter`.
        """
        self.basic_formatter, self.full_formatter = self.full_formatter, self.basic_formatter

    def handle_exception(self):
        """
            Register a exception hook if the logger is capable of logging then to alternate streams.
        """

        def _handle_exception(exc_type, exc_value, exc_traceback):
            """
                Logging uncaught exceptions in Python
                https://stackoverflow.com/questions/6234405/logging-uncaught-exceptions-in-python
            """
            self.critical( "Uncaught exception", exc_info=( exc_type, exc_value, exc_traceback ) )
            sys.__excepthook__( exc_type, exc_value, exc_traceback )

        if ( self.file_handler \
                or self.hasHandlers() ) \
                and self.getEffectiveLevel() != NOTSET:

            sys.excepthook = _handle_exception

    def disable(self):
        """
            Delete all automatically setup handlers created by the automatic `setup()`.
        """

        if self.stream_handler:
            self.removeHandler( self.stream_handler )
            self.stream_handler = None

        if self.file_handler:
            self.removeHandler( self.file_handler )
            self.file_handler.close()
            self.file_handler = None

    def setup(self, file=EMPTY_KWARG, mode=EMPTY_KWARG, delete=EMPTY_KWARG, date=EMPTY_KWARG, level=EMPTY_KWARG,
            function=EMPTY_KWARG, name=EMPTY_KWARG, time=EMPTY_KWARG, msecs=EMPTY_KWARG, tick=EMPTY_KWARG,
            formatter=EMPTY_KWARG, rotation=EMPTY_KWARG, **kwargs):
        """
            If `file` parameter is passed, instead of output the debug to the standard output
            stream, send it a file on the file system, which is faster for large outputs.

            As this function remembers its parameters passed from previous calls, you need to
            explicitly pass `file=None` with `delete=True` if you want to disable the file
            system output after setting up it to log to a file. See the function Debugger::reset()
            for the default parameters values used on this setup utility.

            If the parameters `date`, `level`, `function`, `name`, `time`, `tick` and `msecs` are
            strings nonempty, their value will be used to defining their configuration formatting.
            For example, if you pass name="%(name)s: " the function name will be displayed as
            `name: `, instead of the default `[name] `.

            If you change your `sys.stderr` after creating an StreamHandler, you need to pass `force=True`
            to make it to recreate the StreamHandler because of the old reference to `sys.stderr`.

            Single page cheat-sheet about Python string formatting pyformat.info
            https://github.com/ulope/pyformat.info

            Override a method at instance level
            https://stackoverflow.com/questions/394770/override-a-method-at-instance-level

            @param `file`  a relative or absolute path to the log file. If empty the output
                                will be sent to the standard output stream.

            @param `mode`       the file write mode on the file system. It can be `a` to append to the
                                existent file, or `w` to erase the existent file before start. If the
                                parameter `rotation` is set to non zero, then this will be an integer value
                                setting how many backups are going to be keep when doing the file rotation as
                                specified on logging::handlers::RotatingFileHandler documentation.

            @param `delete`     if True, it will delete the other handler before activate the
                                current one, otherwise it will only activate the selected handler.
                                Useful for enabling multiple handlers simultaneously.

            @param `date`       if True, add to the `full_formatter` the date on the format `%Y-%m-%d`.
            @param `level`      if True, add to the `full_formatter` the log levels.
            @param `function`   if True, add to the `full_formatter` the function name.
            @param `name`       if True, add to the `full_formatter` the logger name.
            @param `time`       if True, add to the `full_formatter` the time on the format `%H:%M:%S:microseconds`.
            @param `msecs`      if True, add to the `full_formatter` the time.perf_counter() difference from the last call.
            @param `tick`       if True, add to the `full_formatter` the time.perf_counter() difference from the last call.
            @param `formatter`  if not None, replace this `full_formatter` by the logging.Formatter() provided.

            @param `rotation`   if non zero, creates a RotatingFileHandler with the specified size
                                in Mega Bytes instead of FileHandler when creating a log file by the
                                `file` option. See logging::handlers::RotatingFileHandler for more information.

            @param `force`      if True (default False), it will force to create the the handlers,
                                even if there are not changes on the current saved default parameters.

            @param `active`     if True (default True), it will not do the setup on the current logger object, but
                                it will find out which one is the active logger and call his setup.
        """
        self._setup( file=file, mode=mode, delete=delete, date=date, level=level,
                function=function, name=name, time=time, msecs=msecs, tick=tick,
                formatter=formatter, rotation=rotation, **kwargs )

    def _setup(self, **kwargs):
        """
            Allow to pass positional arguments to `setup()`.
        """
        force = kwargs.pop( 'force', False )
        active = kwargs.pop( 'active', True )

        has_changes = False
        default_arguments = self.default_arguments

        for kwarg in kwargs:
            value = kwargs[kwarg]

            if value != EMPTY_KWARG:

                if value != default_arguments[kwarg]:
                    has_changes = True
                    default_arguments[kwarg] = value

        if has_changes \
                or force \
                or ( not self.stream_handler \
                    and not self.file_handler ):

            if active:
                logger = self.active() or self

            else:
                logger = self

            self._setup_formatters( logger, default_arguments )
            self._setup_log_handlers( logger, default_arguments )

    @staticmethod
    def _setup_log_handlers(self, default_arguments):

        if default_arguments['file']:
            rotation = default_arguments['rotation']
            self.output_file = self.get_debug_file_path( default_arguments['file'] )

            sys.stderr.write( "".join( self._get_time_prefix( datetime.datetime.now() ) )
                    + "Logging to the file " + self.output_file + "\n" )

            if self.file_handler:
                self.removeHandler( self.file_handler )

            if rotation > 0:
                backup_count = default_arguments['mode']
                backup_count = abs( backup_count ) if isinstance( backup_count, int ) else 2

                rotation = rotation * 1024 * 1024
                self.file_handler = ConcurrentRotatingFileHandler( self.output_file, maxBytes=rotation, backupCount=backup_count )

            else:
                self.file_handler = logging.FileHandler( self.output_file, default_arguments['mode'] )

            self.file_handler.setFormatter( self.full_formatter )
            self.addHandler( self.file_handler )
            self.handle_exception()

            if default_arguments['delete'] \
                    and self.stream_handler:

                self.removeHandler( self.stream_handler )
                self.stream_handler = None

        else:

            if self.stream_handler:
                self.removeHandler( self.stream_handler )

            self.stream_handler = logging.StreamHandler()
            self.stream_handler.setFormatter( self.full_formatter )
            self.addHandler( self.stream_handler )

            if default_arguments['delete'] \
                    and self.file_handler:

                self.removeHandler( self.file_handler )
                self.file_handler.close()
                self.file_handler = None

    def warn(self, msg, *args, **kwargs):
        """
            Fix second indirection created by the super().warn() method, by directly calling _log()
        """

        if self.isEnabledFor( WARNING ):
            self._log( WARNING, msg, args, **kwargs )

    def _log(self, level, msg, args, exc_info=None, extra={}, stack_info=False, debug_level=0):
        self.currentTick = timeit.default_timer()

        debug_level = "(%d)" % debug_level if debug_level else ""
        extra.update( {"debugLevel": debug_level, "tickDifference": self.currentTick - self.lastTick} )

        if is_python2:
            super( Debugger, self )._log( level, msg, args, exc_info, extra )

        else:
            super()._log( level, msg, args, exc_info, extra, stack_info )

        self.lastTick = self.currentTick

    @staticmethod
    def _setup_formatters(self, default_arguments):
        self.clean_formatter = logging.Formatter( "", "" )
        self.basic_formatter = logging.Formatter( "[%(name)s] %(asctime)s:%(msecs)010.6f{} %(message)s".format(
                "" if is_python2 else " %(tickDifference).2e" ), "%H:%M:%S" )

        if default_arguments['formatter']:

            if isinstance( default_arguments['formatter'], logging.Formatter ):
                self.full_formatter = default_arguments['formatter']

            else:
                raise ValueError( "Error: The formatter %s must be an instance of logging.Formatter" % default_arguments['formatter'] )

        else:
            name = self.getFormat( default_arguments, 'name', "[%(name)s] " )
            tick = self.getFormat( default_arguments, 'tick', "%(tickDifference).2e " )

            level    = self.getFormat( default_arguments, 'level', "%(levelname)s%(debugLevel)s " )
            function = self.getFormat( default_arguments, 'function', "%(funcName)s:%(lineno)d " )

            date_format  = self.getFormat( default_arguments, 'date', "%Y-%m-%d " )
            date_format += self.getFormat( default_arguments, 'time', "%H:%M:%S" )

            msecs = self.getFormat( default_arguments, 'msecs', ":%(msecs)010.6f " )

            time  = "%(asctime)s" if len( date_format ) else ""
            time += "" if msecs else " " if default_arguments['time'] else ""

            self.full_formatter = logging.Formatter( "{}{}{}{}{}{}%(message)s".format(
                    name, time, msecs, tick, level, function ), date_format )

    @staticmethod
    def getFormat(default_arguments, setting, default):
        value = default_arguments[setting]

        if isinstance( value, str ):
            return value

        return default if value else ""

    def _get_time_prefix(self, currentTime):
        return [ "[%s]" % self.name,
                " %02d" % currentTime.hour,
                ":%02d" % currentTime.minute,
                ":%02d" % currentTime.second,
                ":%07d " % currentTime.microsecond ]

    def _fixChildren(self):
        """
            When automatically creating loggers, some children logger can be setup before the
            parent logger, if the children logger is instantiated on module level and its module
            is imported before the parent logger to be setup.

            Then this will cause the the both parent and child logger to be setup and have handlers
            outputting data to theirs output stream. Hence, here we fix that by disabling the
            children logger when they are setup before the parent logger.

            This method is only called automatically by this module level function `getLogger()`
            when is set to automatically setup the logger. If you are not using the automatic setup
            you do not need to use this function because you should know what you are doing and how
            you should setup your own loggers.
        """
        loggers = Debugger.manager.loggerDict
        parent_name = self.name
        parent_name_length = len( parent_name )

        for logger_name in loggers:
            logger = loggers[logger_name]

            if not isinstance( logger, PlaceHolder ):

                # i.e., if logger.parent.name.startswith( parent_name )
                if logger.parent.name[:parent_name_length] == parent_name:
                    logger.disable()

    @classmethod
    def get_debug_file_path(cls, output_file):
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
            new_output = "/cygdrive/" + cls.remove_windows_driver_letter( output_file )

        elif "linux" in platform_info \
                and "microsoft" in platform_info:

            new_output = cls.remove_windows_driver_letter( output_file )
            new_output = "/mnt/" + new_output[0].lower() + new_output[1:]

        if os.path.isabs( new_output ):
            output_file = new_output

        else:
            output_file = output_file

        # print( "Debugger, get_debug_file_path, output_file:   " + output_file )
        # print( "Debugger, get_debug_file_path, isabs:         " + str( os.path.isabs( output_file ) ) )
        # print( "Debugger, get_debug_file_path, platform_info: " + platform_info )
        return output_file

    @classmethod
    def remove_windows_driver_letter(cls, output_file):
        output_file = output_file.replace( ":", "", 1 )
        output_file = output_file.replace( "\\", "/", 1 )
        return output_file.replace( "\\\\", "/", 1 )

    @classmethod
    def getRootLogger(cls):
        """
            Return the main root logger `root_debugger` used by this extension of the standard
            logging module.
        """
        return cls.root

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


# Setup the alternate debugger, completely independent of the standard logging module Logger class
root = Debugger( "root_debugger", "WARNING" )
Debugger.root = root

Debugger.manager = Manager( root )
Debugger.manager.setLoggerClass( Debugger )


def getLogger(debug_level=127, logger_name=None,
            file=EMPTY_KWARG, mode=EMPTY_KWARG, delete=EMPTY_KWARG, date=EMPTY_KWARG, level=EMPTY_KWARG,
            function=EMPTY_KWARG, name=EMPTY_KWARG, time=EMPTY_KWARG, msecs=EMPTY_KWARG, tick=EMPTY_KWARG,
            formatter=EMPTY_KWARG, rotation=EMPTY_KWARG, **kwargs):
    """
    Return a logger with the specified name, creating it if necessary. If no name is specified,
    return a new logger based on the main logger file name. See also logging::Manager::getLogger()

    It has the same parameters as Debugger::setup with the addition of the following parameters:

    @param `debug_level` and `logger_name` are the same parameters passed to the Debugger::__init__() constructor.

    @param `level` if True, add to the `full_formatter` the log levels. If not a boolean,
        it should be the initial logging level accordingly to logging::Logger::setLevel(level)

    @param from `file` until `**kwargs` are the named parameters passed to the Debugger.setup() member function.

    @param `setup` if True (default), ensure there is at least one handler enabled in the hierarchy,
        then the current created Logger setup method will be called with `force=True`.
    """
    return _getLogger( debug_level, logger_name,
            file=file, mode=mode, delete=delete, date=date, level=level,
            function=function, name=name, time=time, msecs=msecs, tick=tick,
            formatter=formatter, rotation=rotation, **kwargs )


def _getLogger(debug_level=127, logger_name=None, **kwargs):
    """
        Allow to pass positional arguments to `getLogger()`.
    """
    level = kwargs.get( "level", EMPTY_KWARG )
    debug_level, logger_name = _get_debug_level( debug_level, logger_name )

    logger = Debugger.manager.getLogger( logger_name )
    logger.debug_level = debug_level

    if level != EMPTY_KWARG \
            and not isinstance( level, bool ):

        kwargs.pop( "level" )
        logger.setLevel( level )

    if kwargs.pop( "setup", True ) == True:
        active = logger.active()

        if active:
            active._setup( **kwargs )

        else:
            logger._setup( **kwargs )
            logger._fixChildren()

    return logger


def _get_debug_level(debug_level, logger_name):

    if logger_name:

        if isinstance( logger_name, int ):
            debug_level, logger_name = logger_name, debug_level

            if isinstance( logger_name, int ):
                raise ValueError( "The variable `logger_name` must be an instance of string, instead of `%s`." % str( logger_name ) )

        else:

            if not isinstance( debug_level, int ):
                raise ValueError( "The variable `logger_name` must be an instance of int, instead of `%s`." % logger_name )

    else:

        if isinstance( debug_level, int ):
            logger_name = os.path.basename( __file__ )

        else:
            logger_name = debug_level
            debug_level = 127

    return debug_level, logger_name

