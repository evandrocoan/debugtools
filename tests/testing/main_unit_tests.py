#! /usr/bin/env python
# -*- coding: utf-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2018 @ Evandro Coan
#   Project Unit Tests
#
#  Redistributions of source code must retain the above
#  copyright notice, this list of conditions and the
#  following disclaimer.
#
#  Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials
#  provided with the distribution.
#
#  Neither the name Evandro Coan nor the names of any
#  contributors may be used to endorse or promote products
#  derived from this software without specific prior written
#  permission.
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

import re
import os
import sys

import unittest
import inspect
import traceback


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True

try:
    import sublime_plugin

    import debug_tools
    from debug_tools import utilities
    from debug_tools import testing_utilities
    from debug_tools import TeeNoFile

    # Import and reload the debugger
    # sublime_plugin.reload_plugin( "debug_tools.logger" )
    # sublime_plugin.reload_plugin( "debug_tools.utilities" )
    # sublime_plugin.reload_plugin( "debug_tools.testing_utilities" )

except ImportError:

    def assert_path(*args):
        module = os.path.realpath( os.path.join( *args ) )
        if module not in sys.path:
            sys.path.append( module )

    # Import the debug tools
    assert_path( os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ) ), 'all' )

    import debug_tools
    from debug_tools import utilities
    from debug_tools import testing_utilities
    from debug_tools import TeeNoFile


# We need to keep a global reference to this because the logging module internally grabs an
# reference to the first `sys.strerr` it can get its hands on it.
#
# We could make the logger recreate the `stderr` output StreamHandler by passing `force=True` to
# to `Debugger.setup()`, removing the old reference to `sys.stderr`.
_stderr = TeeNoFile()
_stdout = TeeNoFile(stdout=True)


def getLogger(debug_level=127, logger_name=None, **kwargs):
    global log
    global line
    create_test_file = kwargs.pop( 'create_test_file', "" )

    if create_test_file:
        kwargs['file'] = utilities.get_relative_path( create_test_file, __file__ )

    log = debug_tools.logger.getLogger( debug_level, logger_name, **kwargs )
    _stdout.clear( log )
    _stderr.clear( log )

    frameinfo = inspect.getframeinfo( sys._getframe(1) )
    line = frameinfo.lineno


def log_traceback(ex, ex_traceback=None):
    """
        Best way to log a Python exception
        https://stackoverflow.com/questions/5191830/best-way-to-log-a-python-exception
    """

    if ex_traceback is None:
        ex_traceback = ex.__traceback__

    tb_lines = [ line.rstrip('\n') for line in
                 traceback.format_exception(ex.__class__, ex, ex_traceback)]

    # print( "\n".join( tb_lines ) )
    sys.stderr.write( "\n".join( tb_lines ) )


class StdErrUnitTests(testing_utilities.MultipleAssertionFailures):
    """
        How to assert output with nosetest/unittest in python?
        https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
    """

    def setUp(self):
        super(StdErrUnitTests, self).setUp()

        sys.stderr.write("\n")
        sys.stderr.write("\n")

    def tearDown(self):
        super(StdErrUnitTests, self).tearDown()

        log.clear( True )
        log.reset()

    @unittest.skipIf( sys.version_info < (3,8), "Feature only available in Python 3.8 or above..." )
    def test_find_caller_with_stacklevel(self):
        getLogger( 1, time=0, msecs=0, tick=0 )
        the_level = 1

        def innermost():
            log( 'Something...', stacklevel=the_level )

        def inner():
            innermost()

        def outer():
            _stderr.clear( log )
            inner()

        outer()
        the_level += 1
        self.assertRegexpMatches( _stderr.contents(),
                r"logger.innermost:\d+ - Something..." )

        outer()
        the_level += 1
        self.assertRegexpMatches( _stderr.contents(),
                r"logger.inner:\d+ - Something..." )

        outer()
        the_level += 1
        self.assertRegexpMatches( _stderr.contents(),
                r"logger.outer:\d+ - Something..." )

        outer()
        the_level += 1
        self.assertRegexpMatches( _stderr.contents(),
                r"logger.test_find_caller_with_stacklevel:\d+ - Something..." )

    @unittest.skipIf( sys.version_info >= (3,8), "Feature only available in Python 3.8 or above..." )
    def test_find_caller_with_stacklevel_on_older_versions(self):
        getLogger( 1, time=0, msecs=0, tick=0 )
        log( 'Something...', stacklevel=1 )

        self.assertRegexpMatches( _stderr.contents(),
                r"logger.test_find_caller_with_stacklevel_on_older_versions:\d+ - Something..." )

    def test_function_name(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )
        log.newline()

        def function_name():
            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )

        function_name()
        output = _stderr.contents( r"\d{4}\-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        offset1 = 1
        offset2 = 4

        self.assertEqual( utilities.wrap_text( """\
            testing.main_unit_tests.test_function_name:{} - Bitwise
            testing.main_unit_tests.test_function_name:{} - Bitwise
            testing.main_unit_tests.test_function_name:{} - Warn
            testing.main_unit_tests.test_function_name:{} - Info
            testing.main_unit_tests.test_function_name:{} - Debug

            testing.main_unit_tests.function_name:{} - Bitwise
            testing.main_unit_tests.function_name:{} - Bitwise
            testing.main_unit_tests.function_name:{} - Warn
            testing.main_unit_tests.function_name:{} - Info
            testing.main_unit_tests.function_name:{} - Debug
            """.format(
                    line+offset1+1, line+offset1+2, line+offset1+3, line+offset1+4, line+offset1+5,
                    line+offset2+6, line+offset2+7, line+offset2+8, line+offset2+9, line+offset2+10,
            ) ), output )

    def test_no_function_name_and_level(self):
        getLogger( 127, "testing.main_unit_tests", date=True, function=False, levels=True )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        output = _stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( utilities.wrap_text( """\
            testing.main_unit_tests DEBUG(1) - Bitwise
            testing.main_unit_tests DEBUG(8) - Bitwise
            testing.main_unit_tests WARNING - Warn
            testing.main_unit_tests INFO - Info
            testing.main_unit_tests DEBUG - Debug
            """ ),
            output )

    def test_date_disabled(self):
        getLogger( "testing.main_unit_tests", 127, function=False )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( utilities.wrap_text( """\
            testing.main_unit_tests - Bitwise
            testing.main_unit_tests - Bitwise
            testing.main_unit_tests - Warn
            testing.main_unit_tests - Info
            testing.main_unit_tests - Debug
            """ ),
            output )

    def test_get_logger_empty(self):
        getLogger( function=False )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( utilities.wrap_text( """\
            logger - Bitwise
            logger - Bitwise
            logger - Warn
            logger - Info
            logger - Debug
            """ ),
            output )

    def test_get_logger_more_empty(self):
        getLogger( function=False, name=False )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( utilities.wrap_text( """\
            Bitwise
            Bitwise
            Warn
            Info
            Debug
            """ ),
            output )

    def test_disabled_logger_empty_integer_message(self):
        getLogger( 0 )
        log( 1 )
        log.clean( 1 )
        log.basic( 1 )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( utilities.wrap_text( """\
            """ ),
            output )

    def test_fast_log_setup_activation(self):
        getLogger( 1, fast=True )
        log( 2 )
        log.clean( 4 )
        log.basic( 8 )

        log.setup( fast=False )
        log( 16 )
        log.clean( 32 )
        log.basic( 64 )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} (?:\d\.\d{2}e.\d{2} )?\- " )
        self.assertEqual( utilities.wrap_text( """\
            + logger.test_fast_log_setup_activation:{} - 16
            + 32
            + logger - 64
            """.format( line + 6 ) ),
            output )

    def test_basic_formatter(self):
        getLogger( 127, "testing.main_unit_tests" )
        log.setup_basic( function=True, separator=" " )

        log.basic( 1, "Debug" )

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} " )
        self.assertEqual( "testing.main_unit_tests.test_basic_formatter:{} Debug".format( line + 3 ), output )

    def test_exception_throwing(self):
        getLogger( "testing.main_unit_tests", 127 )

        try:
            raise Exception( "Test Error" )
        except Exception:
            log.exception( "I am catching you" )

        regex_pattern = re.compile( r"File \".*\", line \d+," )
        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
                testing.main_unit_tests.test_exception_throwing:{} - I am catching you
                Traceback (most recent call last):
                   in test_exception_throwing
                    raise Exception( "Test Error" )
                Exception: Test Error
            """.format( line + 5 ) ),
            regex_pattern.sub( "", output ) )

    def test_exception_throwing_from_file(self):
        getLogger( "testing.main_unit_tests", 127, create_test_file='main_unit_tests.txt', stderr=True )

        try:
            log( 1, "I am catching you..." )
            raise Exception( "Test Exception" )

        except Exception as error:

            if is_python2:
                _, _, exception_traceback = sys.exc_info()
                log_traceback( error, exception_traceback )

            else:
                log_traceback( error )

        regex_pattern = re.compile( r"File \".*\"," )
        output = _stderr.file_contents( log, r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
                testing.main_unit_tests.test_exception_throwing_from_file:{} - I am catching you...
                Traceback (most recent call last):
                   line {}, in test_exception_throwing_from_file
                    raise Exception( "Test Exception" )
                Exception: Test Exception
                """.format( line + 3, line + 4  ) ),
            regex_pattern.sub( "", output ) )

    def test_infinity_recursion_fix(self):
        getLogger( 1, 'LSP.boot', create_test_file='main_unit_tests.txt', delete=False, stdout=False, stderr=True )

        log.setup( "", delete=False )
        log( 1, 'No LSP clients enabled.' )

        output = _stderr.file_contents( log, r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( "LSP.boot.test_infinity_recursion_fix:{} - No LSP clients enabled.".format( line + 3 ), output )


class StdOutUnitTests(testing_utilities.MultipleAssertionFailures):

    def setUp(self):
        super(StdOutUnitTests, self).setUp()

        sys.stderr.write("\n")
        sys.stderr.write("\n")

    def tearDown(self):
        super(StdOutUnitTests, self).tearDown()

        log.clear( True )
        log.reset()

    def test_helloWordToStdOut(self):
        getLogger( 127, "testing.main_unit_tests", create_test_file='main_unit_tests.txt', stdout=True )

        print("Std out logging capture test!")
        output = _stdout.file_contents( log, r"" )

        self.assertEqual( "Std out logging capture test!", output )

    def test_stdout_stderr_and_file_loggging(self):
        getLogger( "testing.main_unit_tests", 127, create_test_file='main_unit_tests.txt', stdout=True, stderr=True )

        log( 1, "Before adding StreamHandler" )
        sys.stdout.write("std OUT Before adding StreamHandler\n")
        sys.stderr.write("std ERR Before adding StreamHandler\n")

        log.setup()
        log( 1, "After adding StreamHandler" )
        sys.stdout.write("std OUT After adding StreamHandler\n")
        sys.stderr.write("std ERR After adding StreamHandler\n")

        file_output = _stdout.file_contents( log, r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        stderr_contents = _stderr.contents( r"" )
        stdout_contents = _stdout.contents( r"" )

        self.assertEqual( utilities.wrap_text( """\
                + testing.main_unit_tests.test_stdout_stderr_and_file_loggging:{} - Before adding StreamHandler
                + std OUT Before adding StreamHandler
                + std ERR Before adding StreamHandler
                + testing.main_unit_tests.test_stdout_stderr_and_file_loggging:{} - After adding StreamHandler
                + std OUT After adding StreamHandler
                + std ERR After adding StreamHandler
                """.format( line + 2 , line + 7 ) ), file_output )

        self.assertEqual( utilities.wrap_text( """\
                + std OUT Before adding StreamHandler
                + std OUT After adding StreamHandler
                """.format() ), stdout_contents )

        self.assertEqual( utilities.wrap_text( """\
                + std ERR Before adding StreamHandler
                + std ERR After adding StreamHandler
                """.format() ), stderr_contents )


class LogRecordUnitTests(testing_utilities.MultipleAssertionFailures):
    """
        Test the SmartLogRecord class usage.

        How to assert output with nosetest/unittest in python?
        https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
    """

    def setUp(self):
        super(LogRecordUnitTests, self).setUp()
        sys.stderr.write("\n")
        sys.stderr.write("\n")

    def tearDown(self):
        super(LogRecordUnitTests, self).tearDown()
        log.clear( True )
        log.reset()

    def test_invalid_logger_creation(self):
        getLogger( "testing.main_unit_tests", "testing.main_unit_tests" )
        log('Something...')
        output = _stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertIn("Something...", output)

    def test_dictionaryLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        dictionary = {1: 'defined_chunk'}
        log('dictionary', )
        log('dictionary', dictionary)

        output = _stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
                + testing.main_unit_tests.test_dictionaryLogging:{line1} - dictionary
                + testing.main_unit_tests.test_dictionaryLogging:{line2} - dictionary {{1: 'defined_chunk'}}
            """.format( line1=line+3, line2=line+4 ) ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_nonDictionaryLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        dictionary = {1: 'defined_chunk'}
        log('dictionary', )
        log('dictionary %s', dictionary)

        output = _stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
                + testing.main_unit_tests.test_nonDictionaryLogging:{line1} - dictionary
                + testing.main_unit_tests.test_nonDictionaryLogging:{line2} - dictionary {{1: 'defined_chunk'}}
            """.format( line1=line+3, line2=line+4 ) ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_dictionaryBasicLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        dictionary = {1: 'defined_chunk'}
        log.basic('dictionary', )
        log.basic('dictionary %s', dictionary)

        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \- " )

        self.assertEqual( utilities.wrap_text( """\
                + testing.main_unit_tests - dictionary
                + testing.main_unit_tests - dictionary {{1: 'defined_chunk'}}
            """.format( line1=line+3, line2=line+4 ) ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_dictionaryCleanLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        dictionary = {1: 'defined_chunk'}
        log.clean('dictionary', )
        log.clean('dictionary', dictionary)

        output = _stderr.contents( r"" )

        self.assertEqual( utilities.wrap_text( """\
                + dictionary
                + dictionary {1: 'defined_chunk'}
            """ ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_integerCleanLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        log.clean(1)
        output = _stderr.contents( r"" )

        self.assertEqual( utilities.wrap_text( """\
            1
            """ ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_integerBasicLogging(self):
        getLogger( 127, "testing.main_unit_tests", date=True )

        log.basic(1)
        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \- " )

        self.assertEqual( utilities.wrap_text( """\
            + testing.main_unit_tests - 1
            """ ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_integerFullLogging(self):
        getLogger( 127, "testing.main_unit_tests" )

        log(1)
        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
            + testing.main_unit_tests.test_integerFullLogging:{} - 1
            """.format( line + 2 ) ),
            utilities.wrap_text( output, trim_spaces='+' ) )

    def test_integerFullLoggingEdge(self):
        getLogger( 127, "testing.main_unit_tests" )

        log(2, 2)
        output = _stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( utilities.wrap_text( """\
            + testing.main_unit_tests.test_integerFullLoggingEdge:{} - 2
            """.format( line + 2 ) ),
            utilities.wrap_text( output, trim_spaces='+' ) )


class SetupFormattingSpacingUnitTests(testing_utilities.MultipleAssertionFailures):

    def setUp(self):
        super(SetupFormattingSpacingUnitTests, self).setUp()
        sys.stderr.write("\n")
        sys.stderr.write("\n")

    def tearDown(self):
        super(SetupFormattingSpacingUnitTests, self).tearDown()
        log.clear( True )
        log.reset()

    def test_not_time(self):
        getLogger( 1, time=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_not_time:\d\d\d - Something..." )

    def test_not_time_msecs(self):
        getLogger( 1, time=0, msecs=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d.\d\de(\+|\-)\d\d - logger.test_not_time_msecs:\d\d\d - Something..." )

    def test_not_time_msecs_tick(self):
        getLogger( 1, time=0, msecs=0, tick=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"logger.test_not_time_msecs_tick:\d\d\d - Something..." )

    def test_not_time_msecs_tick_name(self):
        getLogger( 1, time=0, msecs=0, tick=0, name=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"test_not_time_msecs_tick_name:\d\d\d - Something..." )

    def test_not_time_msecs_tick_name_function(self):
        getLogger( 1, time=0, msecs=0, tick=0, name=0, function=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"Something..." )

    def test_not_time_msecs_tick_name_function_but_level(self):
        getLogger( 1, time=0, msecs=0, tick=0, name=0, function=0, levels=1 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"DEBUG\(\d+\) - Something..." )

    def test_not_time_msecs_tick_name_function_level_separator(self):
        getLogger( 1, time=0, msecs=1, tick=0, name=0, function=0, levels=1, separator=0 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d\d.\d\d\d\d\d\dDEBUG\(\d+\)Something..." )

    def test_not_time_msecs_tick_name_function_level_but_separator(self):
        getLogger( 1, time=0, msecs=1, tick=0, name=0, function=0, levels=1, separator=" " )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d\d.\d\d\d\d\d\d DEBUG\(\d+\) Something..." )


class DynamicSetupFormattingUnitTests(testing_utilities.MultipleAssertionFailures):

    def setUp(self):
        super(DynamicSetupFormattingUnitTests, self).setUp()
        sys.stderr.write("\n")
        sys.stderr.write("\n")

    def tearDown(self):
        super(DynamicSetupFormattingUnitTests, self).tearDown()
        log.clear( True )
        log.reset()

    def test_default_logger_creation(self):
        getLogger( 1 )
        log( 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_default_logger_creation:\d\d\d - Something..." )

    def test_logger_name_string_string(self):
        getLogger( "", "mylogger" )
        log( 1, 'Something...' )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - mylogger.test_logger_name_string_string:\d\d\d - Something..." )

    def test_logger_name_string_int(self):
        getLogger( "", 3 )
        log( 1, 'Something...' )
        self.assertEqual( 127, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_string_int:\d\d\d - Something..." )

    def test_logger_name_string_empty(self):
        getLogger( "", "" )
        log( 1, 'Something...' )
        self.assertEqual( 1, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_string_empty:\d\d\d - Something..." )

    def test_logger_name_int_empty(self):
        getLogger( 3, "" )
        log( 1, 'Something...' )
        self.assertEqual( 3, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_int_empty:\d\d\d - Something..." )

    def test_logger_name_int_int(self):
        getLogger( 3, "" )
        log( 1, 'Something...' )
        self.assertEqual( 3, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_int_int:\d\d\d - Something..." )

    def test_logger_name_none_int(self):
        getLogger( None, "" )
        log( 1, 'Something...' )
        self.assertEqual( 1, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_none_int:\d\d\d - Something..." )

    def test_logger_name_empty_none(self):
        getLogger( "", None )
        log( 1, 'Something...' )
        self.assertEqual( 1, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_empty_none:\d\d\d - Something..." )

    def test_logger_name_none_none(self):
        getLogger( None, None )
        log( 1, 'Something...' )
        self.assertEqual( 1, log.debug_level )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d:\d\d\d.\d\d\d\d\d\d \d.\d\de(\+|\-)\d\d - logger.test_logger_name_none_none:\d\d\d - Something..." )

    def test_not_msecs(self):
        getLogger( 1 )
        log( 'Something...', msecs=0 )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d \d.\d\de(\+|\-)\d\d - logger.test_not_msecs:\d\d\d - Something..." )

    def test_not_msecs_tick(self):
        getLogger( 1 )
        log( 'Something...', msecs=0, tick=0 )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"\d\d:\d\d:\d\d - logger.test_not_msecs_tick:\d\d\d - Something..." )

    def test_not_msecs_tick_time(self):
        getLogger( 1 )
        log( 'Something...', msecs=0, tick=0, time=0 )

        output = _stderr.contents()
        self.assertRegexpMatches( output,
                r"logger.test_not_msecs_tick_time:\d\d\d - Something..." )


def load_tests(loader, standard_tests, pattern):
    suite = unittest.TestSuite()
    # suite.addTest( LogRecordUnitTests( 'test_dictionaryBasicLogging' ) )
    # suite.addTest( SetupFormattingSpacingUnitTests( 'test_time' ) )
    suite.addTests( unittest.TestLoader().loadTestsFromTestCase( SetupFormattingSpacingUnitTests ) )
    return suite


# Comment this to run individual Unit Tests
load_tests = None

