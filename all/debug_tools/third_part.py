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
import re
import sys

import stat
import shutil
import datetime

import time
import json
import traceback

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

        while True:

            try:
                with open( file_path, 'r', encoding='utf-8' ) as data_file:
                    return json.load( data_file, object_pairs_hook=OrderedDict )

            except ValueError as error:
                log( 1, "Error: maximum_attempts %d, %s (%s)" % ( maximum_attempts, error, file_path ) )
                maximum_attempts -= 1

                if maximum_attempts < 1:
                    if exceptions:
                        raise

                    else:
                        log.error( "traceback.format_stack():\n%s", "".join( traceback.format_stack() ) )

                    break

                if wait_on_error:
                    time.sleep( 0.1 )

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


def string_convert_list(comma_separated_list):
    """ Given a string as "master," return ["master", ""] """

    if comma_separated_list:
        return [ dependency.strip() for dependency in comma_separated_list.split(',') ]

    return []


def convert_to_pascal_case(input_string):
    """
        how to replace multiple characters in a string?
        https://stackoverflow.com/questions/21859203/how-to-replace-multiple-characters-in-a-string
    """
    clean_string = re.sub( '[=+-:*?"<>|]', ' ', input_string )
    return ''.join( word[0].upper() + word[1:] if len( word ) else word for word in clean_string.split() )


def convert_to_snake_case(pascal_case_name):
    """
        Elegant Python function to convert CamelCase to snake_case?
        https://stackoverflow.com/questions/1175208/elegant-python-function-to-convert-camelcase-to-snake-case
    """
    first_substitution = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', pascal_case_name)
    return re.sub('([a-z0-9])([A-Z])', r'\1_\2', first_substitution).lower()


def compare_text_with_file(input_text, file):
    """
        Return `True` when the provided text and the `file` contents are equal.
    """

    if os.path.exists( file ):

        with open( file, "r", encoding='utf-8' ) as file:
            text = file.read()
            return input_text == text


def add_item_if_not_exists(list_to_append, item):

    if item not in list_to_append:
        list_to_append.append( item )


def add_path_if_not_exists(list_to_add, path):

    if path != "." and path != "..":
        add_item_if_not_exists( list_to_add, path )


def add_git_folder_by_file(file_relative_path, git_folders):
    match = re.search( r"\.git", file_relative_path )

    if match:
        git_folder_relative = file_relative_path[:match.end(0)]

        if git_folder_relative not in git_folders:
            git_folders.append( git_folder_relative )


def is_directory_empty(directory_path):
    """
        How to check to see if a folder contains files using python 3
        https://stackoverflow.com/questions/25675352/how-to-check-to-see-if-a-folder-contains-files-using-python-3
    """
    is_empty = False

    try:
        os.rmdir( directory_path )

    except OSError:
        is_empty = True

    return is_empty


def remove_if_exists(items_list, item):

    if item in items_list:
        items_list.remove( item )


def remove_item_if_exists(list_to_remove, item):

    if item in list_to_remove:
        list_to_remove.remove( item )


def safe_remove(path):

    try:
        os.remove( path )

    except Exception as error:
        log( 1, "Failed to remove `%s`. Error is: %s" % ( path, error) )

        try:
            delete_read_only_file(path)

        except Exception as error:
            log( 1, "Failed to remove `%s`. Error is: %s" % ( path, error) )


def remove_only_if_exists(file_path):

    if os.path.exists( file_path ):
        safe_remove( file_path )


def delete_read_only_file(path):
    _delete_read_only_file( None, path, None )


def _delete_read_only_file(action, name, exc):
    """
        shutil.rmtree to remove readonly files
        https://stackoverflow.com/questions/21261132/shutil-rmtree-to-remove-readonly-files
    """
    os.chmod( name, stat.S_IWRITE )
    os.remove( name )


def remove_git_folder(default_git_folder, parent_folder=None):
    log( 1, "default_git_folder: %s, parent_folder: %s", default_git_folder, parent_folder )
    shutil.rmtree( default_git_folder, ignore_errors=True, onerror=_delete_read_only_file )

    if parent_folder:
        folders_not_empty = []
        recursively_delete_empty_folders( parent_folder, folders_not_empty )

        if len( folders_not_empty ) > 0:
            log( 1, "The installed default_git_folder `%s` could not be removed because is it not empty." % default_git_folder )
            log( 1, "Its files contents are: " + str( os.listdir( default_git_folder ) ) )


def recursively_delete_empty_folders(root_folder, folders_not_empty=[]):
    """
        Recursively descend the directory tree rooted at top, calling the callback function for each
        regular file.

        Python script: Recursively remove empty folders/directories
        https://www.jacobtomlinson.co.uk/2014/02/16/python-script-recursively-remove-empty-folders-directories/

        @param root_folder           the folder to search on
        @param folders_not_empty     a empty python list to put on the deleted folders paths
    """

    try:
        children_folders = os.listdir( root_folder )

        for child_folder in children_folders:
            child_path = os.path.join( root_folder, child_folder )

            if os.path.isdir( child_path ):
                recursively_delete_empty_folders( child_path, folders_not_empty )

                try:
                    os.removedirs( root_folder )
                    is_empty = True

                except OSError:
                    is_empty = False

                    try:
                        _removeEmptyFolders( root_folder )

                    except:
                        pass

                if not is_empty:
                    folders_not_empty.append( child_path )

        os.rmdir( root_folder )

    except:
        pass


def _removeEmptyFolders(path):

    if not os.path.isdir( path ):
        return

    files = os.listdir( path )

    if len( files ):

        for file in files:
            fullpath = os.path.join( path, file )

            if os.path.isdir( fullpath ):
                _removeEmptyFolders( fullpath )

    os.rmdir( path )


def get_immediate_subdirectories(a_dir):
    """
        How to get all of the immediate subdirectories in Python
        https://stackoverflow.com/questions/800197/how-to-get-all-of-the-immediate-subdirectories-in-python
    """
    return [ name for name in os.listdir(a_dir) if os.path.isdir( os.path.join( a_dir, name ) ) ]


def unique_list_join(*lists):
    unique_list = []

    for _list in lists:

        for item in _list:

            if item not in unique_list:
                unique_list.append( item )

    return unique_list


def unique_list_append(a_list, *lists):

    for _list in lists:

        for item in _list:

            if item not in a_list:
                a_list.append( item )


def upcase_first_letter(s):
    return s[0].upper() + s[1:]


def _clean_urljoin(url):

    if url.startswith( '/' ) or url.startswith( ' ' ):
        url = url[1:]
        url = _clean_urljoin( url )

    if url.endswith( '/' ) or url.endswith( ' ' ):
        url = url[0:-1]
        url = _clean_urljoin( url )

    return url


def clean_urljoin(*urls):
    fixed_urls = []

    for url in urls:

        fixed_urls.append( _clean_urljoin(url) )

    return "/".join( fixed_urls )


def convert_to_unix_path(relative_path):
    relative_path = relative_path.replace( "\\", "/" )

    if relative_path.startswith( "/" ):
        relative_path = relative_path[1:]

    return relative_path


def dictionary_to_string_by_line(dictionary):
    variables = \
    [
        "%-50s: %s" % ( variable_name, dictionary[variable_name] )
        for variable_name in dictionary.keys()
    ]

    return "%s" % ( "\n".join( sorted( variables ) ) )


def print_all_variables_for_debugging(dictionary):
    dictionary_lines = dictionary_to_string_by_line( dictionary )
    log( 1, "\nImporting %s settings... \n%s", str(datetime.datetime.now())[0:19], dictionary_lines )


def print_data_file(file_path):
    channel_dictionary = load_data_file( file_path )
    log( 1, "file_data: \n%s", json.dumps( channel_dictionary, indent=4, sort_keys=True ) )

