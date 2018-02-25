
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

    def __init__(self):
        self._contents = []

        self._stderr = sys.stderr
        sys.stderr = self

        # sys.stdout.write( "inspect.getmro(sys.stderr):  %s\n" % str( inspect.getmro( type( sys.stderr ) ) ) )
        # sys.stdout.write( "inspect.getmro(self.stderr): %s\n" % str( inspect.getmro( type( self._stderr ) ) ) )

    def __del__(self):
        """
            python Exception AttributeError: “'NoneType' object has no attribute 'var'”
            https://stackoverflow.com/questions/9750308/python-exception-attributeerror-nonetype-object-has-no-attribute-var
        """
        self.close()

    def clear(self, log):
        log.clear()
        del self._contents[:]

    def flush(self):
        self._stderr.flush()

    def write(self, *args, **kwargs):
        # self._stderr.write( " 111111 %s" % self._stderr.write + str( args ), **kwargs )
        # self._contents.append( " 555555" + str( args ), **kwargs )
        self._stderr.write( *args, **kwargs )
        self._contents.append( *args, **kwargs )

    def contents(self, date_regex):
        contents = self._process_contents( date_regex, "".join( self._contents ) )
        return contents

    def file_contents(self, date_regex, log):

        with io.open( log.output_file, "r", encoding='utf-8' ) as file:
            output = file.read()

        contents = self._process_contents( date_regex, output )
        self._stderr.write("\nContents:\n`%s`\n" % contents)
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
        if sys and self._stderr:
            sys.stderr = self._stderr
            self._stderr = None

