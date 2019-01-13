#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2017-2019 @ Evandro Coan
#   Helper functions and classes not used internally by this package
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

# To run this file, run on the Sublime Text console:
# import imp; import debugtools.all.debug_tools.third_part; imp.reload( debugtools.all.debug_tools.third_part )

import os
import sys

import time
import json

from collections import OrderedDict


# Allow using this file on the website where the sublime module is unavailable
try:
    import sublime

except ImportError:
    sublime = None


try:
    # https://stackoverflow.com/questions/14087598/python-3-importerror-no-module-named-configparser
    import configparser

except( ImportError, ValueError ):
    from six.moves import configparser


try:
    from .logger import getLogger

except( ImportError, ValueError ):
    from logger import getLogger

log = getLogger( 127, __name__ )


def print_python_envinronment():
    index = 0;

    for file_path in sys.path:
        print(index, file_path);
        index += 1;


# print_python_envinronment()
# sys.tracebacklimit = 10; raise ValueError
def assert_path(*args):
    """
        Import a module from a relative path
        https://stackoverflow.com/questions/279237/import-a-module-from-a-relative-path
    """
    module = os.path.realpath( os.path.join( *args ) )
    if module not in sys.path:
        sys.path.append( module )


def get_section_option(section, option, configSettings):
    """
        @param `section` str
        @param `option` str
        @param `configSettings` a ConfigParser object
    """

    if configSettings.has_option( section, option ):
        return configSettings.get( section, option )

    return ""


def open_last_session_data(session_file):
    last_session = configparser.ConfigParser( allow_no_value=True )

    if os.path.exists( session_file ):
        last_session.read( session_file )

    return last_session


def save_session_data(last_section, session_file):

    with open( session_file, 'wt', newline='\n', encoding='utf-8' ) as configfile:
        last_section.write( configfile )


def write_data_file(file_path, channel_dictionary, debug=1):
    """
        Python - json without whitespaces
        https://stackoverflow.com/questions/16311562/python-json-without-whitespaces
    """
    log( 1 & debug, "Writing to the data file: " + str( file_path ) )

    with open( file_path, 'w', newline='\n', encoding='utf-8' ) as output_file:
        json.dump( channel_dictionary, output_file, indent=4, separators=(',', ': ') )
        output_file.write("\n")  # Add newline cause Py JSON does not


def load_package_file_as_binary(file_path, log_level=1):
    packages_start = file_path.find( "Packages" )
    packages_relative_path = file_path[packages_start:].replace( "\\", "/" )

    log( log_level, "packages_relative_path: " + str( packages_relative_path ) )
    resource_bytes = sublime.load_binary_resource( packages_relative_path )
    return resource_bytes


def load_data_file(file_path, wait_on_error=True, log_level=1, exceptions=False):
    """
        Attempt to read the file some times when there is a value error. This could happen when the
        file is currently being written by Sublime Text.

        @return a dictionary object with the JSON file data
    """
    channel_dictionary = OrderedDict()

    if os.path.exists( file_path ):
        maximum_attempts = 10

        while maximum_attempts > 0:

            try:
                with open( file_path, 'r', encoding='utf-8' ) as data_file:
                    return json.load( data_file, object_pairs_hook=OrderedDict )

            except ValueError as error:
                log( 1, "Error: maximum_attempts %d, %s (%s)" % ( maximum_attempts, error, file_path ) )
                maximum_attempts -= 1

                if wait_on_error:
                    time.sleep( 0.1 )

        if maximum_attempts < 1:
            log.exception( "Could not open the file_path: %s" % ( file_path ) )
            if exceptions: raise

    else:

        if sublime:

            try:
                resource_bytes = load_package_file_as_binary( file_path, log_level )
                return json.loads( resource_bytes.decode('utf-8'), object_pairs_hook=OrderedDict )

            except IOError as error:
                log.exception( "Error: The file '%s' does not exists! %s" % ( file_path, error ) )
                if exceptions: raise

        else:

            # Force an exception to be logged by the logging module
            try:
                raise IOError( "Error: The file '%s' does not exists!" % file_path )

            except IOError:
                log.exception( "" )
                if exceptions: raise

    return channel_dictionary

