

try:
    # To run this file, run on the Sublime Text console:
    # import sublime_plugin; sublime_plugin.reload_plugin( "PythonDebugTools.tests.manual_tests" )
    import sublime_plugin

    # Import and reload the debugger
    sublime_plugin.reload_plugin( "debug_tools.logger" )

except:
    pass


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

