
import os
import sys

import unittest


PACKAGE_ROOT_DIRECTORY = os.path.dirname( os.path.realpath( __file__ ) )

loader = unittest.TestLoader()
start_dir = os.path.join( PACKAGE_ROOT_DIRECTORY, 'testing' )

# What numbers can you pass as verbosity in running Python Unit Test Suites?
# https://stackoverflow.com/questions/1322575/what-numbers-can-you-pass-as-verbosity-in-running-python-unit-test-suites
suite = loader.discover( start_dir, "*unit_tests.py" )
runner = unittest.TextTestRunner(verbosity=2)

# print( sys.path )
results = runner.run( suite )

print( "results: %s" % results )
print( "results.wasSuccessful: %s" % results.wasSuccessful() )
sys.exit( not results.wasSuccessful() )


