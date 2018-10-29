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

from debug_tools import getLogger
log = getLogger( 127, __name__ )

from .utilities import wrap_text
from .utilities import DiffMatchPatch
from .utilities import diff_match_patch
from .lockable_type import LockableType


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

    def diffMatchPatchAssertEqual(self, expected, actual, msg=""):
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
            diff_match = DiffMatchPatch()

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

    def assertTextEqual(self, goal, results, msg="", trim_tabs=True, trim_spaces=True, trim_plus=True, trim_lines=False, indent=""):
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

