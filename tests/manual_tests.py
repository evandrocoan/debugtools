

# To run this file, run on the Sublime Text console:
# import sublime_plugin; sublime_plugin.reload_plugin( "PythonDebugTools.tests.manual_tests" )

# Import and reload the debugger
from python_debug_tools.logger import getLogger
import sublime_plugin

sublime_plugin.reload_plugin( "python_debug_tools.logger" )
log = getLogger( 127, __name__ )

log( 1, "My logging" )
log.warn( "A warning" )
log.debug( "A debugging" )

def function_name():
    log( 1, "Bitwise" )
    log( 8, "Bitwise" )
    log.warn( "Warn" )
    log.info( "Info" )
    log.debug( "Debug" )

log.setup_logger( function=False, level=True )
log.insert_empty_line()
function_name()

log.setup_logger( date=True )
log.insert_empty_line()
function_name()

