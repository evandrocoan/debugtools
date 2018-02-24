

try:
    # To run this file, run on the Sublime Text console:
    # import imp; import DebugTools.tests.manual_tests; imp.reload( DebugTools.tests.manual_tests )
    import sublime_plugin

except (ImportError):
    import os
    import sys

    def assert_path(module):

        if module not in sys.path:
            sys.path.append( module )

    # Import the debug tools
    assert_path( os.path.join( os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ) ), 'all' ) )


# Import and reload the debugger
import imp
import debug_tools.logger
imp.reload( debug_tools.logger )

from debug_tools.logger import getLogger

log = getLogger( 127, __name__, date=True )

log( 1, "Bitwise" )
log( 8, "Bitwise" )
log.warn( "Warn" )
log.info( "Info" )
log.debug( "Debug" )

try:
    raise Exception( "Test Error" )
except Exception:
    log.exception( "I am catching you" )

def function_name():
    log( 1, "Bitwise" )
    log( 8, "Bitwise" )
    log.warn( "Warn" )
    log.info( "Info" )
    log.debug( "Debug" )

    try:
        raise Exception( "Test Error" )
    except Exception:
        log.exception( "I am catching you" )

log.reset()
log.setup( function=False, level=True )
log.newline()
function_name()

log.reset()
log = getLogger( __name__, 127 )
log.setup( date=True )
log.newline()
function_name()

log.reset()
log = getLogger( __name__ )
log.setup( date=True )
log.newline()
function_name()

log.reset()
log = getLogger( 127, function=True )
log.setup()
log.newline()
function_name()

log.reset()
log = getLogger()
log.setup()
log.newline()
function_name()

