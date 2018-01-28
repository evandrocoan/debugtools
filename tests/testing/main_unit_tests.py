

import sys
import unittest
import sublime_plugin

# Import and reload the debugger
sublime_plugin.reload_plugin( "debug_tools.logger" )
sublime_plugin.reload_plugin( "debug_tools.utilities" )
from debug_tools.logger import getLogger
from debug_tools.utilities import wrap_text

MODULE_NAME = "testing.main_unit_tests"
MODULE_NAME_LENGTH = len( MODULE_NAME )


# How to assert output with nosetest/unittest in python?
# https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
from contextlib import contextmanager
from io import StringIO

@contextmanager
def captured_output():
    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr

    try:
        sys.stdout, sys.stderr = new_out, new_err
        yield sys.stdout, sys.stderr

    finally:
        sys.stdout, sys.stderr = old_out, old_err


class MainUnitTests(unittest.TestCase):

    @classmethod
    def setUp(self):
        self.maxDiff = None

    def test_function_name(self):

        with captured_output() as (out, err):
            log = getLogger( 127, __name__, date=True )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )

            def function_name():
                log( 1, "Bitwise" )
                log( 8, "Bitwise" )
                log.warn( "Warn" )
                log.info( "Info" )
                log.debug( "Debug" )

            log.newline()
            function_name()

        output = err.getvalue().strip().split( "\n" )
        clean_output = []

        base_date = "2018-01-28 20:29:26:617.002010 3.63e-04"
        base_date_length = len( base_date )

        for line in output:
            clean_output.append( line[MODULE_NAME_LENGTH + base_date_length + 4:] )

        output = "\n".join( clean_output )
        self.assertEqual( wrap_text( """\
                test_function_name:46 Bitwise
                test_function_name:47 Bitwise
                test_function_name:48 Warn
                test_function_name:49 Info
                test_function_name:50 Debug

                function_name:53 Bitwise
                function_name:54 Bitwise
                function_name:55 Warn
                function_name:56 Info
                function_name:57 Debug
                """ ),
                output )

