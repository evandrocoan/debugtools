
import os
import sys

import unittest


PACKAGE_ROOT_DIRECTORY = os.path.dirname( os.path.realpath( __file__ ) )

loader = unittest.TestLoader()
start_dir = os.path.join( PACKAGE_ROOT_DIRECTORY, 'testing' )

suite = loader.discover( start_dir, "*unit_tests.py" )
runner = unittest.TextTestRunner()
results = runner.run( suite )

sys.exit( not results.wasSuccessful() )

