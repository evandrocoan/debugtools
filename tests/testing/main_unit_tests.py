# -*- coding: UTF-8 -*-

import sys
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
    sublime_plugin.reload_plugin( "DebugTools.all.debug_tools.logger" )
    sublime_plugin.reload_plugin( "DebugTools.all.debug_tools.utilities" )

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


new_err = StringIO()
old_err = sys.stderr


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

    def tearDown(self):
        """
            Explain the “setUp” and “tearDown” Python methods used in test cases
            https://stackoverflow.com/questions/6854658/explain-the-setup-and-teardown-python-methods-used-in-test-cases
        """
        new_err.seek(0)
        new_err.truncate(0)

    def getOutput(self, module_name, base_date):
        clean_output = []
        output = new_err.getvalue().strip().split( "\n" )

        base_date_length = len( base_date )
        module_name_length = len( module_name )

        for line in output:
            clean_output.append( line[:module_name_length] + line[module_name_length+base_date_length:] )

        output = "\n".join( clean_output )
        return output

    def test_function_name(self):

        try:
            sys.stderr = new_err
            log = getLogger( 127, "testing.main_unit_tests", date=True, function=True )

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
            sys.stderr = old_err

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
            line      = frameinfo.lineno

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
            sys.stderr = new_err
            log = getLogger( 127, "testing.main_unit_tests", date=True, function=False, level=True )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stderr = old_err

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
            sys.stderr = new_err
            log = getLogger( "testing.main_unit_tests", 127, date=False, function=False )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stderr = old_err

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
            sys.stderr = new_err
            log = getLogger( function=False )

            log( 1, "Bitwise" )
            log( 8, "Bitwise" )
            log.warn( "Warn" )
            log.info( "Info" )
            log.debug( "Debug" )
            log.reset()

        finally:
            sys.stderr = old_err

        output = self.getOutput( "[logger.py] ", "20:29:26:617.002010 3.63e-04 " )
        self.assertEqual( wrap_text( """\
                [logger.py] Bitwise
                [logger.py] Bitwise
                [logger.py] Warn
                [logger.py] Info
                [logger.py] Debug
                """ ),
                output )

