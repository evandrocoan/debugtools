

try:
    # To run this file, run on the Sublime Text console:
    # import imp; import DebugTools.tests.testing.manual_tests; imp.reload( DebugTools.tests.testing.manual_tests )
    import sublime_plugin

except (ImportError):
    pass


# Import and reload the debugger
import imp
import DebugTools.all.debug_tools.logger
imp.reload( DebugTools.all.debug_tools.logger )

from debug_tools.logger import getLogger

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

log.setup( function=False, level=True )
log.newline()
function_name()

log = getLogger( __name__, 127 )
log.setup( date=True )
log.newline()
function_name()

log = getLogger( __name__ )
log.setup( date=True )
log.newline()
function_name()

log = getLogger( 127, function=True )
# log.setup()
log.newline()
function_name()

log = getLogger()
log.setup()
log.newline()
function_name()

