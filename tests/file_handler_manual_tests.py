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
import os
import sys

try:
    # To run this file, run on the Sublime Text console:
    # import imp; import debugtools.tests.file_handler_manual_tests; imp.reload( debugtools.tests.file_handler_manual_tests )
    import sublime_plugin

except (ImportError):

    def assert_path(*args):
        module = os.path.realpath( os.path.join( *args ) )
        if module not in sys.path:
            sys.path.append( module )

    # Import the debug tools
    assert_path( os.path.dirname( os.path.dirname( os.path.dirname( os.path.realpath( __file__ ) ) ) ), 'all' )


# Import and reload the debugger
if sys.version_info < (3,4):
    import imp as reloader
else:
    import importlib as reloader

import debug_tools.logger
reloader.reload( debug_tools.logger )

from debug_tools.logger import getLogger
from debug_tools.utilities import get_relative_path

FILE1 = get_relative_path('file_handler_manual_tests1.txt', __file__)
FILE2 = get_relative_path('file_handler_manual_tests2.txt', __file__)

log = getLogger( 127, "LSP.core", file=FILE1, stdout=True )
# log.setup("")
log('log MODULE 1')

print('Doing std OUT 1')
sys.stderr.write('Doing std ERR 1\n')

log2 = getLogger( 127, "channel.module", file=FILE2, rotation=10, mode=2, stdout=True )
# log2.setup("")
log2('log2 MODULE 1')

print('Doing std OUT 2')
sys.stderr.write('Doing std ERR 2\n')

log('log MODULE 2')
log2('log2 MODULE 2')

# print('log\n%s'%log.handlers)
log = getLogger( 127, __name__, FILE1, rotation=10, mode=2, stdout=True, delete=False)

log2 = getLogger(1, 'LSP.boot', delete=False)
log2.setup( FILE1, delete=False )
log2(1, 'No LSP clients enabled.')

log = getLogger( 1, 'LSP.boot', file=FILE1, delete=False )
log.setup( "", delete=False )
log( 1, 'No LSP clients enabled.' )

# Unlock the files
log.removeHandlers()
log2.removeHandlers()

print('Doing std OUT 3')

