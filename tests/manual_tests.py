

# To run this file, run on the Sublime Text console:
# import sublime_plugin; sublime_plugin.reload_plugin( "PythonDebugTools.tests.manual_tests" )
import sublime_plugin

# Import and reload the debugger
sublime_plugin.reload_plugin( "python_debug_tools.logger" )
from python_debug_tools.logger import getLogger

log = getLogger( 127, __name__ )

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

log.setup_logger( function=False, level=True )
log.insert_empty_line()
function_name()

log = getLogger( __name__, 127 )
log.setup_logger( date=True )
log.insert_empty_line()
function_name()

log = getLogger( __name__ )
log.setup_logger( date=True )
log.insert_empty_line()
function_name()

log = getLogger( 127 )
log.setup_logger()
log.insert_empty_line()
function_name()

log = getLogger()
log.setup_logger()
log.insert_empty_line()
function_name()

