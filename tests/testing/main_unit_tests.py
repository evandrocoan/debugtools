

import sys
import unittest

import sublime_plugin
from io import StringIO


# Import and reload the debugger
sublime_plugin.reload_plugin( "PythonDebugTools.all.debug_tools.logger" )
sublime_plugin.reload_plugin( "PythonDebugTools.all.debug_tools.utilities" )

from PythonDebugTools.all.debug_tools.logger import getLogger
from PythonDebugTools.all.debug_tools.utilities import wrap_text

MODULE_NAME = "[testing.main_unit_tests] "


class MainUnitTests(unittest.TestCase):
    """
        How to assert output with nosetest/unittest in python?
        https://stackoverflow.com/questions/4219717/how-to-assert-output-with-nosetest-unittest-in-python
    """

    new_out, new_err = StringIO(), StringIO()
    old_out, old_err = sys.stdout, sys.stderr

    @classmethod
    def setUp(self):
        self.maxDiff = None

        self.new_out.truncate(0)
        self.new_out.seek(0)

        self.new_err.truncate(0)
        self.new_err.seek(0)

    def getOutput(self, module_name=MODULE_NAME, base_date="2018-01-28 20:29:26:617.002010 3.63e-04 "):
        clean_output = []
        output = self.new_err.getvalue().strip().split( "\n" )

        base_date_length = len( base_date )
        module_name_length = len( module_name )

        for line in output:
            clean_output.append( line[:module_name_length] + line[module_name_length+base_date_length:] )

        output = "\n".join( clean_output )
        return output

    def test_function_name(self):

        try:
            sys.stdout, sys.stderr = self.new_out, self.new_err
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

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput()
        self.assertEqual( wrap_text( """\
                [testing.main_unit_tests] test_function_name:58 Bitwise
                [testing.main_unit_tests] test_function_name:59 Bitwise
                [testing.main_unit_tests] test_function_name:60 Warn
                [testing.main_unit_tests] test_function_name:61 Info
                [testing.main_unit_tests] test_function_name:62 Debug

                [testing.main_unit_tests] function_name:65 Bitwise
                [testing.main_unit_tests] function_name:66 Bitwise
                [testing.main_unit_tests] function_name:67 Warn
                [testing.main_unit_tests] function_name:68 Info
                [testing.main_unit_tests] function_name:69 Debug
                """ ),
                output )


    def test_no_function_name_and_level(self):

        try:
            sys.stdout, sys.stderr = self.new_out, self.new_err
            log = getLogger( 127, __name__, date=True, function=False, level=True )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput()
        self.assertEqual( wrap_text( """\
                [testing.main_unit_tests] DEBUG(1) Bitwise
                [testing.main_unit_tests] DEBUG(8) Bitwise
                [testing.main_unit_tests] WARNING Warn
                [testing.main_unit_tests] INFO Info
                [testing.main_unit_tests] DEBUG Debug
                """ ),
                output )

