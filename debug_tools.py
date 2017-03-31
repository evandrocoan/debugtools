
####################### Licensing #######################################################
#
#   Copyright 2017 @ Evandro Coan
#
#   Originally written on:
#   https://github.com/evandrocoan/SublimeAMXX_Editor/blob/888c6822047d84e2370348b6cf5f4ac509f77b32/AMXXEditor.py#L1741-L1804
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


import datetime
import os

# Uncomment this to save the debugging to a file.
# LOG_FILE_NAME = os.path.abspath('DebugTools.log')


# Debugging
if 'LOG_FILE_NAME' in globals():
    del LOG_FILE_NAME

# LOG_FILE_NAME = os.path.abspath('DebugTools.log')
startTime = datetime.datetime.now()
print_debug_lastTime = startTime.microsecond

# Enable editor debug messages: (bitwise)
#
# 0  - Disabled debugging.
# 1  - Errors messages.
# 2  - Outputs when it starts a file parsing.
# 4  - General messages.
# 63 - All debugging levels at the same time.
g_debug_level = 63



if 'LOG_FILE_NAME' in globals():

    # Clear the log file contents
    open(LOG_FILE_NAME, 'w').close()
    print( "Logging the DebugTools debug to the file " + LOG_FILE_NAME )

    # Setup the logger
    logging.basicConfig( filename=LOG_FILE_NAME, format='%(asctime)s %(message)s', level=logging.DEBUG )

    def print_debug(level, msg) :

        global print_debug_lastTime
        currentTime = datetime.datetime.now().microsecond

        # You can access global variables without the global keyword.
        if g_debug_level & level != 0:

            logging.debug( "[DEBUG] " \
                    + str( currentTime ) \
                    + "%7d " % ( currentTime - print_debug_lastTime ) \
                    + msg )

            print_debug_lastTime = currentTime

else:

    def print_debug(level, msg) :

        global print_debug_lastTime
        currentTime = datetime.datetime.now().microsecond

        # You can access global variables without the global keyword.
        if g_debug_level & level != 0:

            print( "[DEBUG] " \
                    + "%02d" % datetime.datetime.now().hour + ":" \
                    + "%02d" % datetime.datetime.now().minute + ":" \
                    + "%02d" % datetime.datetime.now().second + ":" \
                    + str( currentTime ) \
                    + "%7d " % ( currentTime - print_debug_lastTime ) \
                    + msg )

            print_debug_lastTime = currentTime







