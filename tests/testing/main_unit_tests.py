# -*- coding: UTF-8 -*-

import sys
import re
import unittest

from inspect import currentframe, getframeinfo


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True
    from StringIO import StringIO

else:
    from io import StringIO


try:
    import sublime_plugin

    from DebugTools.all.debug_tools.logger import getLogger
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

    from debug_tools.logger import getLogger
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
        del self._contents[:]

    def flush(self):
        self._stderr.flush()

    def write(self, data):
        self._stderr.write( data )
        self._contents.append( data )

    def contents(self, date_regex):
        clean_output = []
        date_regex_pattern = re.compile( date_regex )

        output = "".join( self._contents )
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
# recreate the StreamHandler removing the old reference to `sys.stderr`.
stderr = TeeNoFile()


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

    def test_function_name(self):
        stderr.clear()
        log = getLogger( 127, "testing.main_unit_tests", date=True )

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
        log.reset()

        output = stderr.contents( r"\d{4}\-\d{2}-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e\-\d{2} \- " )

        frameinfo = getframeinfo(currentframe())
        line      = frameinfo.lineno

        offset1 = -21
        offset2 = -18

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
        stderr.clear()
        log = getLogger( 127, "testing.main_unit_tests", date=True, function=False, level=True )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        log.newline()
        log.reset()

        output = stderr.contents( r"\d{4}\-\d{2}\-\d{2} \d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e\-\d{2} \- " )
        self.assertEqual( wrap_text( """\
            testing.main_unit_tests DEBUG(1) - Bitwise
            testing.main_unit_tests DEBUG(8) - Bitwise
            testing.main_unit_tests WARNING - Warn
            testing.main_unit_tests INFO - Info
            testing.main_unit_tests DEBUG - Debug
            """ ),
            output )

    def test_date_disabled(self):
        stderr.clear()
        log = getLogger( "testing.main_unit_tests", 127, function=False )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        log.newline()
        log.reset()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e\-\d{2} \- " )
        self.assertEqual( wrap_text( """\
            testing.main_unit_tests - Bitwise
            testing.main_unit_tests - Bitwise
            testing.main_unit_tests - Warn
            testing.main_unit_tests - Info
            testing.main_unit_tests - Debug
            """ ),
            output )

    def test_get_logger_empty(self):
        stderr.clear()
        log = getLogger( function=False )

        log( 1, "Bitwise" )
        log( 8, "Bitwise" )
        log.warn( "Warn" )
        log.info( "Info" )
        log.debug( "Debug" )

        log.newline()
        log.reset()

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e\-\d{2} \- " )
        self.assertEqual( wrap_text( """\
            logger.py{python2} - Bitwise
            logger.py{python2} - Bitwise
            logger.py{python2} - Warn
            logger.py{python2} - Info
            logger.py{python2} - Debug
            """.format( python2="c" if is_python2 else "" ) ),
            output )

    def test_exception_throwing(self):
        stderr.clear()
        log = getLogger( "testing.main_unit_tests", 127 )

        try:
            raise Exception( "Test Error" )
        except Exception:
            log.exception( "I am catching you" )

        log.newline()
        log.reset()

        frameinfo = getframeinfo(currentframe())
        line      = frameinfo.lineno

        regex_pattern = re.compile( r"File \".*\", line \d+," )

        output = stderr.contents( r"\d{2}:\d{2}:\d{2}:\d{3}\.\d{6} \d\.\d{2}e\-\d{2} \- " )
        self.assertEqual( wrap_text( """\
                testing.main_unit_tests.test_exception_throwing:{} - I am catching you
                Traceback (most recent call last):
                   in test_exception_throwing
                    raise Exception( "Test Error" )
                Exception: Test Error            """.format( line - 5 ) ),
            regex_pattern.sub( "", output ) )

