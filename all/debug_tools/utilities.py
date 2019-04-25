#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

####################### Licensing #######################################################
#
#   Copyright 2017-2019 @ Evandro Coan
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

# To run this file, run on the Sublime Text console:
# import imp; import debugtools.all.debug_tools.utilities; imp.reload( debugtools.all.debug_tools.utilities )

import os
import io
import re
import sys

import time
import random

import threading
import textwrap

from collections import OrderedDict

try:
    from natsort import natsorted

except( ImportError, ValueError ):

    def natsorted(*args, **kwargs):
        raise RuntimeError( "The library natsort is required to run this function.\nYou can install it with `pip install natsort`" )

try:
    import diff_match_patch

except( ImportError, ValueError ):
    diffmatchpatch = None
    diff_match_patch = None


is_python2 = False

if sys.version_info[0] < 3:
    is_python2 = True
    Event = threading._Event

else:
    Event = threading.Event

class SleepEvent(Event):

    def __init__(self):
        super( SleepEvent, self ).__init__()

    def sleep(self, timeout=None):
        """
            If blockOnSleepCall() was called before, this will sleep the current thread for ever if
            not arguments are passed. Otherwise, it accepts a positive floating point number for
            seconds in which this thread will sleep.

            If disableSleepCall() is called before the timeout has passed, it will immediately get
            out of sleep and this thread will wake up.
        """
        self.wait( timeout )

    def blockOnSleepCall(self):
        self.clear()

    def disableSleepCall(self):
        self.set()


if is_python2:
    # Based on Python 3's textwrap.indent
    def textwrap_indent(text, prefix, predicate=None):
        """Adds 'prefix' to the beginning of selected lines in 'text'.
        If 'predicate' is provided, 'prefix' will only be added to the lines
        where 'predicate(line)' is True. If 'predicate' is not provided,
        it will default to adding 'prefix' to all non-empty lines that do not
        consist solely of whitespace characters.
        """
        if predicate is None:
            def predicate(line):
                return line.strip()

        def prefixed_lines():
            for line in text.splitlines(True):
                yield (prefix + line if predicate(line) else line)
        return u"".join(prefixed_lines())

else:
    textwrap_indent = textwrap.indent


if diff_match_patch:

    if is_python2:
        # Bail out at 65535 because unichr(65536) throws.
        _g_maximum_lines = 40000
        _g_char_limit = 65535
    else:
        unichr = chr

        # Bail out at 1114111 because unichr(1114112) throws.
        _g_maximum_lines = 666666
        _g_char_limit = 1114111

    class diffmatchpatch(diff_match_patch.diff_match_patch):

        def diff_prettyText(self, diffs):
            """Convert a diff array into a pretty Text report.
            Args:
              diffs: Array of diff tuples.
            Returns:
              Text representation.
            """
            last_text = "\n"
            last_op_type = self.DIFF_EQUAL

            results_diff = []
            cut_next_new_line = [False]

            # print('\ndiffs:\n%s\n' % diffs)
            operations = (self.DIFF_INSERT, self.DIFF_DELETE)

            def parse(sign):
                # print('new1:', text.encode( 'ascii' ))

                if text:
                    new = text

                else:
                    return ''

                new = textwrap_indent( "%s" % new, sign, lambda line: True )

                # force the diff change to show up on a new line for highlighting
                if len(results_diff) > 0:
                    new = '\n' + new

                if new[-1] == '\n':

                    if op == self.DIFF_INSERT and next_text and new[-1] == '\n' and next_text[0] == '\n':
                        cut_next_new_line[0] = True;

                        # Avoids a double plus sign showing up when the diff has the element (1, '\n')
                        if len(text) > 1: new = new + '%s\n' % sign

                elif next_op not in operations and next_text and next_text[0] != '\n':
                    new = new + '\n'

                # print('new2:', new.encode( 'ascii' ))
                return new

            for index in range(len(diffs)):
                op, text = diffs[index]
                if index < len(diffs) - 1:
                    next_op, next_text = diffs[index+1]
                else:
                    next_op, next_text = (0, "")

                if op == self.DIFF_INSERT:
                    results_diff.append( parse( "+ " ) )

                elif op == self.DIFF_DELETE:
                    results_diff.append( parse( "- " ) )

                elif op == self.DIFF_EQUAL:
                    # print('new3:', text.encode( 'ascii' ))
                    # if last_op_type != op or last_text and last_text[-1] == '\n': text = textwrap_indent(text, "  ")
                    text = textwrap_indent(text, "  ")

                    if cut_next_new_line[0]:
                        cut_next_new_line[0] = False
                        text = text[1:]

                    results_diff.append(text)
                    # print('new4:', text.encode( 'ascii' ))

                last_text = text
                last_op_type = op

            return "".join(results_diff)

        def diff_linesToWords(self, text1, text2, delimiter=re.compile('\n')):
            """
                Split two texts into an array of strings.  Reduce the texts to a string
                of hashes where each Unicode character represents one line.

                95% of this function code is copied from `diff_linesToChars` on:
                    https://github.com/google/diff-match-patch/blob/895a9512bbcee0ac5a8ffcee36062c8a79f5dcda/python3/diff_match_patch.py#L381

                Copyright 2018 The diff-match-patch Authors.
                https://github.com/google/diff-match-patch
                Licensed under the Apache License, Version 2.0 (the "License");
                you may not use this file except in compliance with the License.
                You may obtain a copy of the License at
                  http://www.apache.org/licenses/LICENSE-2.0

                Args:
                    text1: First string.
                    text2: Second string.
                    delimiter: a re.compile() expression for the word delimiter type

                Returns:
                    Three element tuple, containing the encoded text1, the encoded text2 and
                    the array of unique strings.  The zeroth element of the array of unique
                    strings is intentionally blank.
            """
            lineArray = []  # e.g. lineArray[4] == "Hello\n"
            lineHash = {}   # e.g. lineHash["Hello\n"] == 4

            # "\x00" is a valid character, but various debuggers don't like it.
            # So we'll insert a junk entry to avoid generating a null character.
            lineArray.append('')

            def diff_linesToCharsMunge(text):
                """Split a text into an array of strings.  Reduce the texts to a string
                of hashes where each Unicode character represents one line.
                Modifies linearray and linehash through being a closure.
                Args:
                    text: String to encode.
                Returns:
                    Encoded string.
                """
                chars = []
                # Walk the text, pulling out a substring for each line.
                # text.split('\n') would would temporarily double our memory footprint.
                # Modifying text would create many large strings to garbage collect.
                lineStart = 0
                lineEnd = -1
                while lineEnd < len(text) - 1:
                    lineEnd = delimiter.search(text, lineStart)

                    if lineEnd:
                        lineEnd = lineEnd.start()

                    else:
                        lineEnd = len(text) - 1

                    line = text[lineStart:lineEnd + 1]

                    if line in lineHash:
                        chars.append(unichr(lineHash[line]))
                    else:
                        if len(lineArray) == maxLines:
                            # Bail out at maxLines because unichr(maxLines+1) throws.
                            line = text[lineStart:]
                            lineEnd = len(text)
                        lineArray.append(line)
                        lineHash[line] = len(lineArray) - 1
                        chars.append(unichr(len(lineArray) - 1))
                    lineStart = lineEnd + 1
                return "".join(chars)

            # Allocate 2/3rds of the space for text1, the rest for text2.
            maxLines = _g_maximum_lines
            chars1 = diff_linesToCharsMunge(text1)
            maxLines = _g_char_limit
            chars2 = diff_linesToCharsMunge(text2)
            return (chars1, chars2, lineArray)


# An unique identifier for any created object
initial_hash = random.getrandbits( 32 )

def get_unique_hash():
    """
        Generates an unique identifier which can be used to uniquely identify distinct object
        instances.
    """
    global initial_hash

    initial_hash += 1
    return initial_hash


def pop_dict_last_item(dictionary):
    """
        Until python 3.5 the popitem() has has a bug where it does not accepts the last=False argument
        https://bugs.python.org/issue24394 TypeError: popitem() takes no keyword arguments, then,
        automatically detect which one we have here:
        https://docs.python.org/3/library/collections.html#collections.OrderedDict.popitem
    """
    dictionary.popitem(last=True)

try:
    {1: 'a'}.popitem(last=True)

except TypeError:

    def pop_dict_last_item(dictionary):
        dictionary.popitem()


def move_to_dict_beginning(dictionary, key):
    """
        Move a OrderedDict item to its beginning, or add it to its beginning.

        Compatible with Python 2.7
        https://stackoverflow.com/questions/16664874/how-to-add-an-element-to-the-beginning-of-an-ordereddict
    """

    if is_python2:
        value = dictionary[key]
        del dictionary[key]
        root = dictionary._OrderedDict__root

        first = root[1]
        root[1] = first[0] = dictionary._OrderedDict__map[key] = [root, first, key]
        dict.__setitem__(dictionary, key, value)

    else:
        dictionary.move_to_end( key, last=False )


def get_relative_path(relative_path, script_file):
    """
        Computes a relative path for a file on the same folder as this class file declaration.
        https://stackoverflow.com/questions/4381569/python-os-module-open-file-above-current-directory-with-relative-path
    """
    basepath = os.path.dirname( script_file )
    filepath = os.path.abspath( os.path.join( basepath, relative_path ) )
    return filepath


def join_path(*args):
    """ Call join path and then abspath on the result. """
    return os.path.abspath( os.path.join( *args ) )


def get_duplicated_elements(elements_list):
    """
        Given an `elements_list` with duplicated elements, return a set only with the duplicated
        elements in the list. If there are not duplicated elements, an empty set is returned.

        How do I find the duplicates in a list and create another list with them?
        https://stackoverflow.com/questions/9835762/how-do-i-find-the-duplicates-in-a-list-and-create-another-list-with-them
    """
    visited_elements = set()
    visited_and_duplicated = set()

    add_item_to_visited_elements = visited_elements.add
    add_item_to_visited_and_duplicated = visited_and_duplicated.add

    for item in elements_list:

        if item in visited_elements:
            add_item_to_visited_and_duplicated(item)

        else:
            add_item_to_visited_elements(item)

    return visited_and_duplicated


def emquote_string(string):
    """
        Return a string escape into single or double quotes accordingly to its contents.
    """
    string = str( string )
    is_single = "'" in string
    is_double = '"' in string

    if is_single and is_double:
        return '"{}"'.format( string.replace( "'", "\\'" ) )

    if is_single:
        return '"{}"'.format( string )

    return "'{}'".format( string )


def sort_dictionary_lists(dictionary):
    """
        Give a dictionary, call `sorted` on all its elements.
    """

    for key, value in dictionary.items():
        dictionary[key] = sorted( value )

    return dictionary


def sort_alphabetically_and_by_length(iterable):
    """
        Give an `iterable`, sort its elements accordingly to the following criteria:
            1. Sorts normally by alphabetical order
            2. Sorts by descending length

        How to sort by length of string followed by alphabetical order?
        https://stackoverflow.com/questions/4659524/how-to-sort-by-length-of-string-followed-by-alphabetical-order
    """
    return sorted( sorted( natsorted( iterable, key=lambda item: str( item ).lower() ),
                          key=lambda item: str( item ).istitle() ),
                  key=lambda item: len( str( item ) ) )


def sort_correctly(iterable):
    """
        Sort the given iterable in the way that humans expect.

        How to sort alpha numeric set in python
        https://stackoverflow.com/questions/2669059/how-to-sort-alpha-numeric-set-in-python
    """
    convert = lambda text: int( text ) if text.isdigit() else text
    alphanum_key = lambda key: [convert( characters ) for characters in re.split( '([0-9]+)', str( key ).lower() )]
    return sorted( sorted( iterable, key=alphanum_key ), key=lambda item: str( item ).istitle() )


def sort_dictionary(dictionary):
    return OrderedDict( sorted( dictionary.items() ) )


def sort_dictionaries_on_list(list_of_dictionaries):
    sorted_dictionaries = []

    for dictionary in list_of_dictionaries:
        sorted_dictionaries.append( sort_dictionary( dictionary ) )

    return sorted_dictionaries


def sort_list_of_dictionaries(list_of_dictionaries):
    """
        How do I sort a list of dictionaries by values of the dictionary in Python?
        https://stackoverflow.com/questions/72899/how-do-i-sort-a-list-of-dictionaries-by-values-of-the-dictionary-in-python

        case-insensitive list sorting, without lowercasing the result?
        https://stackoverflow.com/questions/10269701/case-insensitive-list-sorting-without-lowercasing-the-result
    """
    sorted_dictionaries = sort_dictionaries_on_list( list_of_dictionaries )
    return sorted( sorted_dictionaries, key=lambda k: k['name'].lower() )


def get_largest_item_size(iterable):
    """
        Given a iterable, get the size/length of its largest key value.
    """
    largest_key = 0

    for key in iterable:

        if len( key ) > largest_key:
            largest_key = len( key )

    return largest_key


def dictionary_to_string(dictionary):
    """
        Given a dictionary with a list for each string key, call `sort_dictionary_lists()` and
        return a string representation by line of its entries.
    """

    if not len( dictionary ):
        return " No elements found."

    strings = []
    elements_strings = []

    dictionary = sort_dictionary_lists( dictionary )
    largest_key = get_largest_item_size( dictionary.keys() ) + 1

    for key, values in dictionary.items():
        elements_strings.clear()

        for item in values:
            elements_strings.append( "{}".format( str( item ) ) )

        strings.append( "{:>{largest_key}}: {}".format( str( key ), " ".join( elements_strings ),
                largest_key=largest_key ) )

    return "\n".join( strings )


def convert_to_text_lines(iterable, use_repr=True, new_line=True, sort=None):
    """
        Given a dictionary with a list for each string key, call `sort_dictionary_lists()` and
        return a string representation by line of its entries.
    """

    if isinstance( iterable, dict):
        return dictionary_to_string( iterable )

    if not iterable:
        return " No elements found."

    strings = []

    if sort:
        iterable = sort( iterable )

    else:
        iterable = sort_alphabetically_and_by_length( iterable )

    for item in iterable:
        strings.append( " {}".format( repr( item ) ) )

    return ( "\n" if new_line else "" ).join( strings )


def getCleanSpaces(inputText, minimumLength=0, lineCutTrigger="", keepSpaceSepators=False):
    """
        Removes spaces and comments from the input expression.

        `minimumLength` of a line to not be ignored
        `lineCutTrigger` all lines after a line starting with this string will be ignored
        `keepSpaceSepators` if True, it will keep at a single space between sentences as `S S`, given `S    S`
    """

    if keepSpaceSepators:
        removeNewSpaces = ' '.join( inputText.split( ' ' ) )
        lineCutTriggerNew = ' '.join( lineCutTrigger.split( ' ' ) ).strip( ' ' )

    else:
        removeNewSpaces = re.sub( r"\t| ", "", inputText )
        lineCutTriggerNew = re.sub( r"\t| ", "", lineCutTrigger )

    # print( "%s" % ( inputText ) )
    lines = removeNewSpaces.split( "\n" )
    clean_lines = []

    for line in lines:

        if keepSpaceSepators:
            line = line.strip( ' ' )

        if minimumLength:

            if len( line ) < minimumLength:
                continue

        if lineCutTrigger:

            if line.startswith( lineCutTriggerNew ):
                break

        if line.startswith( "#" ):
            continue

        clean_lines.append( line )

    return clean_lines


def wrap_text(text, wrap=0, trim_tabs=None, trim_spaces=None, trim_lines=None,
        trim_plus='+', indent="", single_lines=False):
    """
        1. Remove input text leading common indentation, trailing white spaces
        2. If `wrap`, wraps big lists on 80 characters
        3. If `trim_tabs`, replace all tabs this value
        4. If `trim_spaces`, remove this leading symbols
        5. If `trim_lines`, replace all new line characters by this value
        5. If `indent`, the subsequent indent to use
        6. If `trim_plus`, remove this leading symbols
        7. If `single_lines`, remove single new lines but keep consecutive new lines
    """
    clean_lines = []

    if not isinstance( text, str ):
        text = str( text )

    if trim_tabs is not None:
        text = text.replace( '\t', trim_tabs )

    dedent_lines = textwrap.dedent( text ).strip( '\n' )

    if trim_spaces and trim_plus:

        for line in dedent_lines.split( '\n' ):
            line = line.rstrip( trim_spaces ).lstrip( trim_plus )
            clean_lines.append( line )

    elif trim_spaces:

        for line in dedent_lines.split( '\n' ):
            line = line.rstrip( trim_spaces )
            clean_lines.append( line )

    elif trim_plus:

        for line in dedent_lines.split( '\n' ):
            line = line.lstrip( trim_plus )
            clean_lines.append( line )

    if trim_spaces is not None or trim_plus is not None:
        dedent_lines = textwrap.dedent( "\n".join( clean_lines ) )

    if wrap:
        clean_lines.clear()

        for line in dedent_lines.split( '\n' ):
            line = textwrap.fill( line, width=wrap, subsequent_indent=indent )
            clean_lines.append( line )

        dedent_lines = "\n".join( clean_lines )

    if trim_lines is not None:
        dedent_lines = trim_lines.join( dedent_lines.split( '\n' ) )

    if single_lines:
        dedent_lines = re.sub( r'(?<!\n)\n(?!\n)', ' ', dedent_lines)

    return dedent_lines


def get_representation(self, ignore=[], emquote=False, repr=repr):
    """
        Given a object, iterating through all its public attributes and return then as a string
        representation.

        `ignore` a list of attributes to be ignored
        `emquote` if True, puts the attributes values inside single or double quotes accordingly.
        `repr` is the callback to call recursively on nested objects, can be either `repr` or `str`.
    """
    valid_attributes = self.__dict__.keys()
    clean_attributes = []

    if emquote:

        def pack_attribute(string):
            return emquote_string( string )

    else:

        def pack_attribute(string):
            return string

    for attribute in valid_attributes:

        if not attribute.startswith( '_' ) and attribute not in ignore:
            clean_attributes.append( "{}: {}".format( attribute, pack_attribute( self.__dict__[attribute] ) ) )

    return "%s %s;" % ( self.__class__.__name__, ", ".join( clean_attributes ) )


def _create_stdout_handler():
    """
        Call this method to create a copy of this stream model as `stdout_replacement.py`
        using the `sys.stdout` instead of `sys.stderr`.
    """
    model_relative_path = get_relative_path( 'stderr_replacement.py', __file__ )
    destine_relative_path = get_relative_path( 'stdout_replacement.py', __file__ )

    warning_message = wrap_text(
    """
    \"\"\"
        This file is generated automatically based `stderr_replacement.py` while `debug_tools`
        library/package is being developed.

        If you developing the `debug_tools` library, please do not edit this file, but the file
        `stderr_replacement.py` and run `logger.py` function `create_stdout_handler()` by
        uncommenting it on `all/debug_tools/logger.py` file.
    \"\"\"
    """ )

    sys.stderr.write( '\nCreating the `stdout_replacement.py` file!\n' )
    sys.stderr.write( 'model_relative_path %s\n' % model_relative_path )
    sys.stderr.write( 'destine_relative_path %s\n' % destine_relative_path )

    # https://stackoverflow.com/questions/29151181/writing-an-ascii-string-as-binary-in-python
    # https://stackoverflow.com/questions/33054527/python-3-5-typeerror-a-bytes-like-object-is-required-not-str-when-writing-t
    with io.open(model_relative_path, 'rb') as model_file:
        model_text = model_file.read().decode('utf-8')

        with io.open(destine_relative_path, 'wb') as destine_file:
            model_text = model_text.replace( 'stderr', 'stdout' )
            model_text = model_text.replace( '# Warning message here', warning_message )
            destine_file.write( model_text.encode() )

