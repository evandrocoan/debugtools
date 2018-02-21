# -*- coding: UTF-8 -*-

import re
import io
import os

import sys
import unittest
import traceback

from inspect import getframeinfo


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True
    from StringIO import StringIO

else:
    from io import StringIO


try:
    import sublime_plugin

    import debug_tools.logger
    from DebugTools.all.debug_tools.utilities import wrap_text

    # Import and reload the debugger
    sublime_plugin.reload_plugin( "debug_tools.logger" )
    sublime_plugin.reload_plugin( "debug_tools.utilities" )

except ImportError:
    import os
    import sys

    def assert_path(module):

        if module not in sys.path:
            sys.path.append( module )

    # Import the debug tools
    assert_path( os.path.join( os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ) ), 'all' ) )

    import debug_tools.logger
    from debug_tools.utilities import wrap_text


class TeeNoFile(object):
    """
        How do I duplicate sys.stdout to a log file in python?
        https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python
    """

    def __init__(self):
        self._contents = []

        self._stderr = sys.stderr
        sys.stderr = self

    def __del__(self):
        """
            python Exception AttributeError: “'NoneType' object has no attribute 'var'”
            https://stackoverflow.com/questions/9750308/python-exception-attributeerror-nonetype-object-has-no-attribute-var
        """
        self.close()

    def clear(self):
        log.clear()
        del self._contents[:]

    def flush(self):
        self._stderr.flush()

    def write(self, *args, **kwargs):
        # self._stderr.write( " 111111 %s" % self._stderr.write + str( args ), **kwargs )
        # self._contents.append( " 555555" + str( args ), **kwargs )
        self._stderr.write( *args, **kwargs )
        self._contents.append( *args, **kwargs )

    def contents(self, date_regex):
        contents = self._process_contents( date_regex, "".join( self._contents ) )
        return contents

    def file_contents(self, date_regex):

        with io.open( log.output_file, "r", encoding='utf-8' ) as file:
            output = file.read()

        contents = self._process_contents( date_regex, output )
        print("Contents:\n`%s`" % contents)
        return contents

    def _process_contents(self, date_regex, output):
        clean_output = []
        date_regex_pattern = re.compile( date_regex )

        output = output.strip().split( "\n" )

        for line in output:
            clean_output.append( date_regex_pattern.sub( "", line ) )

        return "\n".join( clean_output )

    def close(self):

        # On shutdown `__del__`, the sys module can be already set to None.
        if sys and self._stderr:
            sys.stderr = self._stderr
            self._stderr = None


# We need to keep a global reference to this because the logging module internally grabs an
# reference to the first `sys.strerr` it can get its hands on it.
#
# We could make the logger recreate the `stderr` output StreamHandler by passing `force=True` to
# to `Debugger.setup()`, removing the old reference to `sys.stderr`.
stderr = TeeNoFile()


def getLogger(debug_level=127, logger_name=None, **kwargs):
    global log
    global line
    log = debug_tools.logger.getLogger( debug_level, logger_name, **kwargs )
    stderr.clear()

    frameinfo = getframeinfo( sys._getframe(1) )
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


class MainUnitTests(unittest.TestCase):
    """
        How to assert output with nosetest/unittest in python?
        https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
    """

    def setUp(self):
        """
            how do I clear a stringio object?
            https://stackoverflow.com/questions/4330812/how-do-i-clear-a-stringio-object
        """
        self.maxDiff = None
        sys.stderr.write("\n")

    def tearDown(self):
        log.clear( True )
        log.reset()

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
            log.newline()

        function_name()
        output = stderr.contents( r"\d{4}\-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        offset1 = 1
        offset2 = 4

        self.assertEqual( wrap_text( """\
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
        getLogger( 127, "testing.main_unit_tests", date=True, function=False, level=True )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )
        log.newline()

        output = stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( wrap_text( """\
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
        log.newline()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( wrap_text( """\
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
        log.newline()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( wrap_text( """\
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
        log.newline()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( wrap_text( """\
            Bitwise
            Bitwise
            Warn
            Info
            Debug
            """ ),
            output )

    def test_basic_formatter(self):
        getLogger( 127, "testing.main_unit_tests" )
        log.setup_basic( function=True, separator=" " )

        log.basic( 1, "Debug" )
        log.newline()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )
        self.assertEqual( "testing.main_unit_tests.test_basic_formatter:{} Debug".format( line + 3 ), output )

    def test_exception_throwing(self):
        getLogger( "testing.main_unit_tests", 127 )

        try:
            raise Exception( "Test Error" )
        except Exception:
            log.exception( "I am catching you" )
            log.newline()

        regex_pattern = re.compile( r"File \".*\", line \d+," )
        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

        self.assertEqual( wrap_text( """\
                testing.main_unit_tests.test_exception_throwing:{} - I am catching you
                Traceback (most recent call last):
                   in test_exception_throwing
                    raise Exception( "Test Error" )
                Exception: Test Error            """.format( line + 5 ) ),
            regex_pattern.sub( "", output ) )

    def test_exception_throwing_from_relative_file_path(self):
        getLogger( "testing.main_unit_tests", 127, file="debug_tools_log_test_exception_throwing_from_relative_file_path.txt" )
        throw_file_exception( self )

    def test_exception_throwing_from_absolute_file_path(self):
        getLogger( "testing.main_unit_tests", 127, file=os.path.abspath("debug_tools_log_test_exception_throwing_from_absolute_file_path.txt") )
        throw_file_exception( self )


def throw_file_exception(self):
    line = getframeinfo( sys._getframe(0) ).lineno

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
    output = stderr.file_contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e.\d{2} \- " )

    self.assertEqual( wrap_text( """\
            testing.main_unit_tests.throw_file_exception:{} - I am catching you...
            Traceback (most recent call last):
               line {}, in throw_file_exception
                raise Exception( "Test Exception" )
            Exception: Test Exception            """.format( line + 3, line + 4  ) ),
        regex_pattern.sub( "", output ) )

