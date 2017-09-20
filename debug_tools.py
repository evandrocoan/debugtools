
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


# Debugging
if 'LOG_FILE_NAME' in globals():
    del LOG_FILE_NAME


# Uncomment this to save the debugging to a file.
# LOG_FILE_NAME = os.path.abspath('D:/User/Downloads/tree.txt')


if 'LOG_FILE_NAME' in globals():

    # Clear the log file contents
    open(LOG_FILE_NAME, 'w').close()
    print( "Logging the DebugTools debug to the file " + LOG_FILE_NAME )

    # Setup the logger
    logging.basicConfig( filename=LOG_FILE_NAME, format='%(asctime)s %(message)s', level=logging.DEBUG )

    def _log(_level, level, currentTime, lastTime, debugger_name, msg) :

        # You can access global variables without the global keyword.
        if _level & level != 0:

            # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
            logging.debug( "[%s] " % debugger_name \
                    + str( currentTime.microsecond ) \
                    + "%7d " % ( currentTime.microsecond - lastTime.microsecond ) \
                    + "".join([str( m ) for m in msg]) )

else:

    def _log(_level, level, currentTime, lastTime, debugger_name, msg) :

        # You can access global variables without the global keyword.
        if _level & level != 0:

            # https://stackoverflow.com/questions/45427500/how-to-print-list-inside-python-print
            print( "[%s] " % debugger_name \
                    + "%02d" % currentTime.hour + ":" \
                    + "%02d" % currentTime.minute + ":" \
                    + "%02d" % currentTime.second + ":" \
                    + str( currentTime.microsecond ) \
                    + "%7d " % ( currentTime.microsecond - lastTime.microsecond ) \
                    + "".join([str( m ) for m in msg]) )



class Debugger():

    # Enable debug messages: (bitwise)
    #
    # 0  - Disabled debugging.
    # 1  - Errors messages.
    _level   = 0

    startTime = datetime.datetime.now()
    lastTime  = startTime

    def __init__(self):
        self.debugger_name = os.path.basename( __file__ )

    def __init__(self, file_name):
        self.debugger_name = os.path.basename( file_name )

    def __init__(self, log_level, file_name):
        self._level        = log_level
        self.debugger_name = os.path.basename( file_name )

    def __call__(self, level, *msg):
        currentTime = datetime.datetime.now()

        _log( self._level, level, currentTime, self.lastTime, self.debugger_name, msg )
        self.lastTime = currentTime


