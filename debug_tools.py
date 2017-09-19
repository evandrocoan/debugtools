
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
import logging
import os


debugger_name = os.path.basename( __file__ )

# Debugging
if 'LOG_FILE_NAME' in globals():
    del LOG_FILE_NAME


# Uncomment this to save the debugging to a file.
# LOG_FILE_NAME = os.path.abspath('D:/User/Downloads/tree.txt')


startTime = datetime.datetime.now()
print_debug_lastTime = startTime.microsecond


# Enable debug messages: (bitwise)
#
# 0  - Disabled debugging.
# 1  - Errors messages.
g_debug_level = 0



if 'LOG_FILE_NAME' in globals():

    # Clear the log file contents
    open(LOG_FILE_NAME, 'w').close()
    print( "Logging the DebugTools debug to the file " + LOG_FILE_NAME )

    # Setup the logger
    logging.basicConfig( filename=LOG_FILE_NAME, format='%(asctime)s %(message)s', level=logging.DEBUG )

    def log(level, *msg) :

        global print_debug_lastTime
        currentTime = datetime.datetime.now().microsecond

        # You can access global variables without the global keyword.
        if g_debug_level & level != 0:

            # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
            logging.debug( "[%s] " % debugger_name \
                    + str( currentTime ) \
                    + "%7d " % ( currentTime - print_debug_lastTime ) \
                    + "".join([str( m ) for m in msg]) )

            print_debug_lastTime = currentTime

else:

    def log(level, *msg) :

        global print_debug_lastTime
        currentTime = datetime.datetime.now().microsecond

        # You can access global variables without the global keyword.
        if g_debug_level & level != 0:

            # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
            print( "[%s] " % debugger_name \
                    + "%02d" % datetime.datetime.now().hour + ":" \
                    + "%02d" % datetime.datetime.now().minute + ":" \
                    + "%02d" % datetime.datetime.now().second + ":" \
                    + str( currentTime ) \
                    + "%7d " % ( currentTime - print_debug_lastTime ) \
                    + "".join([str( m ) for m in msg]) )

            print_debug_lastTime = currentTime







