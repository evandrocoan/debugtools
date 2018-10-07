#!/usr/bin/env python3
# -*- coding: UTF-8 -*-

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
import re
import sys

import time
import random

import threading
import textwrap

try:
    from natsort import natsorted

except( ImportError, ValueError ):

    def natsorted(*args, **kwargs):
        raise RuntimeError( "The library natsort is required to run this function.\nYou can install it with `pip install natsort`" )

try:
    import diff_match_patch

except( ImportError, ValueError ):
    diff_match_patch = None


if sys.version_info[0] < 3:
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


if diff_match_patch:

    class DiffMatchPatch(diff_match_patch.diff_match_patch):

        def diff_prettyText(self, diffs):
            """Convert a diff array into a pretty Text report.
            Args:
              diffs: Array of diff tuples.
            Returns:
              Text representation.
            """
            results_diff = []
            cut_next_new_line = [False]
            # print('\ndiffs:\n%s\n' % diffs)

            def parse(sign):
                # print('new1:', text.encode( 'ascii' ))

                if text:
                    new = text

                else:
                    return ''

                new = textwrap.indent( "%s" % new, sign, lambda line: True )

                # force the diff change to show up on a new line for highlighting
                if len(results_diff) > 0:
                    new = '\n' + new

                if new and new[-1] == '\n':

                    if sign == '+ ' and next_text and new[-1] == '\n' and next_text[0] == '\n':
                        cut_next_new_line[0] = True;

                        # Avoids a double plus sign showing up when the diff has the element (1, '\n')
                        if len(text) > 1: new = new + '%s\n' % sign

                    if sign == '- ': new = new[0:-1] + '\n'

                # print('new2:', new.encode( 'ascii' ))
                return new

            for index in range(len(diffs)):
                op, text = diffs[index]
                if index < len(diffs) - 1: next_op, next_text = diffs[index+1]

                if op == self.DIFF_INSERT:
                    results_diff.append( parse( "+ " ) )

                elif op == self.DIFF_DELETE:
                    results_diff.append( parse( "- " ) )

                elif op == self.DIFF_EQUAL:
                    # print('new3:', text.encode( 'ascii' ))
                    text = textwrap.indent(text, "  ")

                    if cut_next_new_line[0]:
                        cut_next_new_line[0] = False
                        text = text[1:]

                    results_diff.append(text)
                    # print('new4:', text.encode( 'ascii' ))

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
                        chars.append(chr(lineHash[line]))
                    else:
                        if len(lineArray) == maxLines:
                            # Bail out at 1114111 because chr(1114112) throws.
                            line = text[lineStart:]
                            lineEnd = len(text)
                        lineArray.append(line)
                        lineHash[line] = len(lineArray) - 1
                        chars.append(chr(len(lineArray) - 1))
                    lineStart = lineEnd + 1
                return "".join(chars)

            # Allocate 2/3rds of the space for text1, the rest for text2.
            maxLines = 666666
            chars1 = diff_linesToCharsMunge(text1)
            maxLines = 1114111
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


def get_relative_path(relative_path, script_file):
    """
        Computes a relative path for a file on the same folder as this class file declaration.
        https://stackoverflow.com/questions/4381569/python-os-module-open-file-above-current-directory-with-relative-path
    """
    basepath = os.path.dirname( script_file )
    filepath = os.path.abspath( os.path.join( basepath, relative_path ) )
    return filepath


def assure_existing_key(dictionary, key, default_value):
    """
        If the given `key` is not present on the `dictionary`, then add it with the `default_value`.
    """

    if key not in dictionary:
        dictionary[key] = default_value


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


def wrap_text(text, wrap=0, trim_tabs=False, trim_spaces=False, trim_lines=False, indent="", trim_plus=True):
    """
        1. Remove input text leading common indentation, trailing white spaces
        2. If `wrap`, wraps big lists on 80 characters.
        3. if `trim_tabs` replace tabs with 2 spaces.
        4. If `trim_spaces`, remove leading ' ' symbols
        5. If `trim_lines`, remove all new line characters.
        5. If `indent`, the subsequent indent to use.
        6. If `trim_plus`, remove leading '+' symbols and if `trim_tabs` replace tabs with 2 spaces.
    """
    clean_lines = []

    if not isinstance( text, str ):
        text = str( text )

    if trim_tabs:
        text = text.replace( '\t', '  ' )

    dedent_lines = textwrap.dedent( text ).strip( '\n' )

    if trim_spaces and trim_plus:

        for line in dedent_lines.split( '\n' ):
            line = line.rstrip( ' ' ).lstrip( '+' )
            clean_lines.append( line )

    elif trim_spaces:

        for line in dedent_lines.split( '\n' ):
            line = line.rstrip( ' ' )
            clean_lines.append( line )

    elif trim_plus:

        for line in dedent_lines.split( '\n' ):
            line = line.lstrip( '+' )
            clean_lines.append( line )

    if trim_spaces or trim_plus:
        dedent_lines = textwrap.dedent( "\n".join( clean_lines ) )

    if wrap:
        clean_lines.clear()

        for line in dedent_lines.split( '\n' ):
            line = textwrap.fill( line, width=wrap, subsequent_indent=indent )
            clean_lines.append( line )

        dedent_lines = "\n".join( clean_lines )

    if trim_lines:
        dedent_lines = "".join( dedent_lines.split( '\n' ) )

    return dedent_lines


def get_representation(self, ignore=[], emquote=False):
    """
        Given a object, iterating through all its public attributes and return then as a string
        representation.

        `ignore` a list of attributes to be ignored
        `emquote` if True, puts the attributes values inside single or double quotes accordingly.
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



