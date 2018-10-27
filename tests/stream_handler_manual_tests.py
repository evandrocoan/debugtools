#! /usr/bin/env python
# -*- coding: utf-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2018 @ Evandro Coan
#   Helper functions and classes
#
#  Redistributions of source code must retain the above
#  copyright notice, this list of conditions and the
#  following disclaimer.
#
#  Redistributions in binary form must reproduce the above
#  copyright notice, this list of conditions and the following
#  disclaimer in the documentation and/or other materials
#  provided with the distribution.
#
#  Neither the name Evandro Coan nor the names of any
#  contributors may be used to endorse or promote products
#  derived from this software without specific prior written
#  permission.
#
#  This program is free software; you can redistribute it and/or modify it
#  under the terms of the GNU General Public License as published by the
#  Free Software Foundation; either version 3 of the License, or ( at
#  your option ) any later version.
#
#  This program is distributed in the hope that it will be useful, but
#  WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
#  General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################################
#

try:
    # To run this file, run on the Sublime Text console:
    # import imp; import DebugTools.tests.stream_handler_manual_tests; imp.reload( DebugTools.tests.stream_handler_manual_tests )
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

