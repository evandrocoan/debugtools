#! /usr/bin/env python
# -*- coding: utf-8 -*-

#
# Licensing
#
# Unit Tests Utilities
# Copyright (C) 2018 Evandro Coan <https://github.com/evandrocoan>
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

import os
import re

import difflib
import unittest
import traceback

from debug_tools import getLogger
log = getLogger( 127, __name__ )

from .utilities import wrap_text
from .utilities import diffmatchpatch
from .utilities import diff_match_patch
from .lockable_type import LockableType


class AssertionErrorData(object):

    def __init__(self, stacktrace, message):
        super(AssertionErrorData, self).__init__()
        self.stacktrace = stacktrace
        self.message = message


class MultipleAssertionFailures(unittest.TestCase):

    def __init__(self, *args, **kwargs):
        self.verificationErrors = []

        # https://thingspython.wordpress.com/2010/09/27/another-super-wrinkle-raising-typeerror/
        self.cached_super = super(MultipleAssertionFailures, self)
        self.cached_super.__init__( *args, **kwargs )

    def tearDown(self):
        self.cached_super.tearDown()

        if self.verificationErrors:
            index = 0
            errors = []

            for error in self.verificationErrors:
                index += 1
                errors.append( "%s\nAssertionError %s: %s" % ( error.stacktrace, index, error.message ) )

            self.fail( '\n\n' + "\n".join( errors ) )
            self.verificationErrors.clear()

    def assertEqual(self, goal, results, msg=None):

        try:
            self.cached_super.assertEqual( goal, results, msg )

        except unittest.TestCase.failureException as error:

            try:
                goodtraces = self._goodStackTraces()
                self.verificationErrors.append( AssertionErrorData( "\n".join( goodtraces[:-2] ), error ) )

            except Exception as exception:
                badtraces = traceback.format_list( traceback.extract_stack() )
                self.verificationErrors.append( AssertionErrorData( "".join( badtraces[:-2] ), str(error) + '\n' + str(exception) ) )

    def _goodStackTraces(self):
        """
            Get only the relevant part of stacktrace.
        """
        stop = False
        found = False
        goodtraces = []

        # stacktrace = traceback.format_exc()
        # stacktrace = traceback.format_stack()
        stacktrace = traceback.extract_stack()

        # https://stackoverflow.com/questions/54499367/how-to-correctly-override-testcase-assertequal
        for stack in stacktrace:
            filename = stack.filename

            if found and not stop and not filename.find( 'lib' ) < filename.find( 'unittest' ):
                stop = True

            if not found and filename.find( 'lib' ) < filename.find( 'unittest' ):
                found = True

            if stop and found:
                stackline = '  File "%s", line %s, in %s\n    %s' % ( stack.filename, stack.lineno, stack.name, stack.line )
                goodtraces.append( stackline )

        return goodtraces


class TestingUtilities(unittest.TestCase):
    """
        Holds common features across all Unit Tests.
    """
    ## Set the maximum size of the assertion error message when Unit Test fail
    maxDiff = None

    ## Whether `characters diff=0`, `words diff=1` or `lines diff=2` will be used
    diffMode = 0

    def __init__(self, *args, **kwargs):
        diffMode = kwargs.pop('diffMode', -1)
        if diffMode > -1: self.diffMode = diffMode

        super(TestingUtilities, self).__init__(*args, **kwargs)

    def setUp(self):
        if diff_match_patch: self.addTypeEqualityFunc(str, self.assertTextEqual)
        super(TestingUtilities, self).setUp()

    def diffMatchPatchAssertEqual(self, expected, actual, msg=None):
        """
            How to wrap correctly the unit testing diff?
            https://stackoverflow.com/questions/52682351/how-to-wrap-correctly-the-unit-testing-diff
        """
        # print( '\n\nexpected\n%s' % expected )
        # print( '\n\nactual\n%s' % actual )

        # print( goal.encode( 'ascii' ) )
        # print( results.encode( 'ascii' ) )

        # self.unidiff_output( goal, results )
        if expected != actual:
            diff_match = diffmatchpatch()

            if self.diffMode == 0:
                diffs = diff_match.diff_main(expected, actual)

            else:
                diff_struct = diff_match.diff_linesToWords(expected, actual,
                        re.compile(r'\b| ') if self.diffMode == 1 else re.compile(r'\n|\r\n') )

                lineText1 = diff_struct[0] # .chars1;
                lineText2 = diff_struct[1] # .chars2;
                lineArray = diff_struct[2] # .lineArray;

                diffs = diff_match.diff_main(lineText1, lineText2, False);
                diff_match.diff_charsToLines(diffs, lineArray);
                diff_match.diff_cleanupSemantic(diffs)

            if msg:
                msg += '\n'

            else:
                msg = "The strings does not match...\n"

            self.fail( msg + diff_match.diff_prettyText(diffs) )

    def tearDown(self):
        """
            Called right after each Unit Test finish its execution, to clean up settings values.
        """
        LockableType.USE_STRING = True
        super(TestingUtilities, self).tearDown()

    def assertTextEqual(self, goal, results, msg=None, trim_tabs=True, trim_spaces=True, trim_plus=True, trim_lines=False, indent=""):
        """
            Remove both input texts indentation and trailing white spaces, then assertEquals() both
            of the inputs.
        """
        goal = wrap_text( goal, trim_tabs=trim_tabs, trim_spaces=trim_spaces,
                trim_plus=trim_plus, indent=indent, trim_lines=trim_lines )

        results = wrap_text( results, trim_tabs=trim_tabs, trim_spaces=trim_spaces,
                trim_plus=trim_plus, indent=indent, trim_lines=trim_lines )

        if diff_match_patch:
            self.diffMatchPatchAssertEqual( goal, results, msg=msg )

        else:
            super( TestingUtilities, self ).assertEqual( goal, results, msg )

    def unidiff_output(self, expected, actual):
        """
            Helper function. Returns a string containing the unified diff of two multiline strings.

            https://stackoverflow.com/questions/845276/how-to-print-the-comparison-of-two-multiline-strings-in-unified-diff-format
            https://stackoverflow.com/questions/15864641/python-difflib-comparing-files
            https://stackoverflow.com/questions/32359402/comparison-of-multi-line-strings-in-python-unit-test
        """
        expected = expected.splitlines( 1 )
        actual = actual.splitlines( 1 )

        # diff = difflib.ndiff( expected, actual )
        if expected != actual:
            diff = difflib.context_diff( expected, actual, fromfile='expected input', tofile='actual output', lineterm='\n' )
            self.fail( '\n' + ''.join( diff ) )

