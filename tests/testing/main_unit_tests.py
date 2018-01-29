

import sys
import unittest

import sublime_plugin

from io import StringIO
from inspect import currentframe, getframeinfo


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True

# Import and reload the debugger
sublime_plugin.reload_plugin( "PythonDebugTools.all.debug_tools.logger" )
sublime_plugin.reload_plugin( "PythonDebugTools.all.debug_tools.utilities" )

from PythonDebugTools.all.debug_tools.logger import getLogger
from PythonDebugTools.all.debug_tools.utilities import wrap_text


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

    def getOutput(self, module_name, base_date):
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
            log.reset()

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput( "[testing.main_unit_tests] ", "2018-01-28 20:29:26:617.002010 3.63e-04 " )

        if is_python2:
            self.assertEqual( wrap_text( """\
                    [testing.main_unit_tests] (unknown function):0 Bitwise
                    [testing.main_unit_tests] (unknown function):0 Bitwise
                    [testing.main_unit_tests] (unknown function):0 Warn
                    [testing.main_unit_tests] (unknown function):0 Info
                    [testing.main_unit_tests] (unknown function):0 Debug

                    [testing.main_unit_tests] (unknown function):0 Bitwise
                    [testing.main_unit_tests] (unknown function):0 Bitwise
                    [testing.main_unit_tests] (unknown function):0 Warn
                    [testing.main_unit_tests] (unknown function):0 Info
                    [testing.main_unit_tests] (unknown function):0 Debug
                    """ ),
                    output )

        else:
            frameinfo = getframeinfo(currentframe())
            frameinfo.lineno

            line = frameinfo.lineno
            offset1 = -40
            offset2 = -38

            self.assertEqual( wrap_text( """\
                    [testing.main_unit_tests] test_function_name:{} Bitwise
                    [testing.main_unit_tests] test_function_name:{} Bitwise
                    [testing.main_unit_tests] test_function_name:{} Warn
                    [testing.main_unit_tests] test_function_name:{} Info
                    [testing.main_unit_tests] test_function_name:{} Debug

                    [testing.main_unit_tests] function_name:{} Bitwise
                    [testing.main_unit_tests] function_name:{} Bitwise
                    [testing.main_unit_tests] function_name:{} Warn
                    [testing.main_unit_tests] function_name:{} Info
                    [testing.main_unit_tests] function_name:{} Debug
                    """.format(
                            line+offset1+1, line+offset1+2, line+offset1+3, line+offset1+4, line+offset1+5,
                            line+offset2+6, line+offset2+7, line+offset2+8, line+offset2+9, line+offset2+10,
                    ) ), output )

    def test_no_function_name_and_level(self):

        try:
            sys.stdout, sys.stderr = self.new_out, self.new_err
            log = getLogger( 127, __name__, date=True, function=False, level=True )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput( "[testing.main_unit_tests] ", "2018-01-28 20:29:26:617.002010 3.63e-04 " )
        self.assertEqual( wrap_text( """\
                [testing.main_unit_tests] DEBUG(1) Bitwise
                [testing.main_unit_tests] DEBUG(8) Bitwise
                [testing.main_unit_tests] WARNING Warn
                [testing.main_unit_tests] INFO Info
                [testing.main_unit_tests] DEBUG Debug
                """ ),
                output )

    def test_date_disabled(self):

        try:
            sys.stdout, sys.stderr = self.new_out, self.new_err
            log = getLogger( __name__, 127, date=False, function=False )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput( "[testing.main_unit_tests] ", "20:29:26:617.002010 3.63e-04 " )
        self.assertEqual( wrap_text( """\
                [testing.main_unit_tests] Bitwise
                [testing.main_unit_tests] Bitwise
                [testing.main_unit_tests] Warn
                [testing.main_unit_tests] Info
                [testing.main_unit_tests] Debug
                """ ),
                output )

    def test_get_logger_empty(self):

        try:
            sys.stdout, sys.stderr = self.new_out, self.new_err
            log = getLogger( function=False )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stdout, sys.stderr = self.old_out, self.old_err

        output = self.getOutput( "[logger.py] ", "20:29:26:617.002010 3.63e-04 " )
        self.assertEqual( wrap_text( """\
                [logger.py] Bitwise
                [logger.py] Bitwise
                [logger.py] Warn
                [logger.py] Info
                [logger.py] Debug
                """ ),
                output )

