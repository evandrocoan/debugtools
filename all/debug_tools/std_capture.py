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

import io
import re
import sys

import inspect
import traceback


class TeeNoFile(object):
    """
        How do I duplicate sys.stdout to a log file in python?
        https://stackoverflow.com/questions/616645/how-do-i-duplicate-sys-stdout-to-a-log-file-in-python
    """
    __closed = False

    def __init__(self, stdout=False, ignoredefault=False):
        """ If `ignoredefault` is True, only write to this object stream.
        """
        self._contents = []
        self.stdout_type = stdout

        if stdout:
            self._std_original = sys.stdout
            sys.stdout = self

        else:
            self._std_original = sys.stderr
            sys.stderr = self

        if ignoredefault:
            self.write = self.writethis
        else:
            self.write = self.writeboth

        # sys.stdout.write( "inspect.getmro(sys.stderr):  %s\n" % str( inspect.getmro( type( sys.stderr ) ) ) )
        # sys.stdout.write( "inspect.getmro(self.stderr): %s\n" % str( inspect.getmro( type( self._std_original ) ) ) )

    @property
    def closed(self):
        """
            @return `True` if the file has been closed.
        """
        return self.__closed

    def __del__(self):
        """
            The try/except block is in case this is called at program exit time, when it's possible
            that globals have already been deleted, and then the close() call might fail.  Since
            there's nothing we can do about such failures and they annoy the end users, we suppress
            the traceback.
            https://github.com/python/cpython/blob/1fd06f1eca80dcbf3a916133919482a8327f3da4/Lib/_pyio.py#L380

            python Exception AttributeError: “'NoneType' object has no attribute 'var'”
            https://stackoverflow.com/questions/9750308/python-exception-attributeerror-nonetype-object-has-no-attribute-var
        """

        try:
            self.close()

        except:
            pass

    def clear(self, log=None):
        if log is not None:
            log.clear()
        del self._contents[:]

    def flush(self):

        try:
            self._std_original.flush()

        except AttributeError:

            if self.closed:
                pass

            else:
                raise

    def writeboth(self, *args, **kwargs):
        # self._std_original.write( " 111111 %s" % self._std_original.write + str( args ), **kwargs )
        # self._contents.append( " 555555" + str( args ), **kwargs )
        self._std_original.write( *args, **kwargs )
        self._contents.append( *args, **kwargs )

    def writethis(self, *args, **kwargs):
        self._contents.append( *args, **kwargs )

    write = writeboth

    def contents(self, date_regex=""):
        contents = self._process_contents( date_regex, "".join( self._contents ) )
        return contents

    def file_contents(self, log, date_regex=""):

        with io.open( log.output_file, "r", encoding='utf-8', newline=None ) as file:
            output = file.read()

        contents = self._process_contents( date_regex, output )
        self._std_original.write("\nContents:\n`%s`\n" % contents)
        return contents

    def _process_contents(self, date_regex, output):
        clean_output = []
        date_regex_pattern = re.compile( date_regex )

        output = output.strip().split( "\n" )

        for line in output:
            clean_output.append( date_regex_pattern.sub( "", line ) )

        return "\n".join( clean_output )

    def close(self):

        # On shutdown `__del__`, the sys module can be already set to None.
        if sys and self._std_original and not self.__closed:

            try:
                self.flush()

            finally:
                self.__closed = True

                if self.stdout_type:
                    sys.stdout = self._std_original

                else:
                    sys.stderr = self._std_original

                self._std_original = None
