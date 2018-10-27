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

import sys


_stderr_default = sys.stderr
_stderr_default_class_type = type( _stderr_default )


class StdErrReplamentHidden(_stderr_default_class_type):
    """
        Which special methods bypasses __getattribute__ in Python?
        https://stackoverflow.com/questions/12872695/which-special-methods-bypasses-getattribute-in-python
    """

    if hasattr( _stderr_default, "__abstractmethods__" ):
        __abstractmethods__ = _stderr_default.__abstractmethods__

    if hasattr( _stderr_default, "__base__" ):
        __base__ = _stderr_default.__base__

    if hasattr( _stderr_default, "__bases__" ):
        __bases__ = _stderr_default.__bases__

    if hasattr( _stderr_default, "__basicsize__" ):
        __basicsize__ = _stderr_default.__basicsize__

    if hasattr( _stderr_default, "__call__" ):
        __call__ = _stderr_default.__call__

    if hasattr( _stderr_default, "__class__" ):
        __class__ = _stderr_default.__class__

    if hasattr( _stderr_default, "__delattr__" ):
        __delattr__ = _stderr_default.__delattr__

    if hasattr( _stderr_default, "__dict__" ):
        __dict__ = _stderr_default.__dict__

    if hasattr( _stderr_default, "__dictoffset__" ):
        __dictoffset__ = _stderr_default.__dictoffset__

    if hasattr( _stderr_default, "__dir__" ):
        __dir__ = _stderr_default.__dir__

    if hasattr( _stderr_default, "__doc__" ):
        __doc__ = _stderr_default.__doc__

    if hasattr( _stderr_default, "__eq__" ):
        __eq__ = _stderr_default.__eq__

    if hasattr( _stderr_default, "__flags__" ):
        __flags__ = _stderr_default.__flags__

    if hasattr( _stderr_default, "__format__" ):
        __format__ = _stderr_default.__format__

    if hasattr( _stderr_default, "__ge__" ):
        __ge__ = _stderr_default.__ge__

    if hasattr( _stderr_default, "__getattribute__" ):
        __getattribute__ = _stderr_default.__getattribute__

    if hasattr( _stderr_default, "__gt__" ):
        __gt__ = _stderr_default.__gt__

    if hasattr( _stderr_default, "__hash__" ):
        __hash__ = _stderr_default.__hash__

    if hasattr( _stderr_default, "__init__" ):
        __init__ = _stderr_default.__init__

    if hasattr( _stderr_default, "__init_subclass__" ):
        __init_subclass__ = _stderr_default.__init_subclass__

    if hasattr( _stderr_default, "__instancecheck__" ):
        __instancecheck__ = _stderr_default.__instancecheck__

    if hasattr( _stderr_default, "__itemsize__" ):
        __itemsize__ = _stderr_default.__itemsize__

    if hasattr( _stderr_default, "__le__" ):
        __le__ = _stderr_default.__le__

    if hasattr( _stderr_default, "__lt__" ):
        __lt__ = _stderr_default.__lt__

    if hasattr( _stderr_default, "__module__" ):
        __module__ = _stderr_default.__module__

    if hasattr( _stderr_default, "__mro__" ):
        __mro__ = _stderr_default.__mro__

    if hasattr( _stderr_default, "__name__" ):
        __name__ = _stderr_default.__name__

    if hasattr( _stderr_default, "__ne__" ):
        __ne__ = _stderr_default.__ne__

    if hasattr( _stderr_default, "__new__" ):
        __new__ = _stderr_default.__new__

    if hasattr( _stderr_default, "__prepare__" ):
        __prepare__ = _stderr_default.__prepare__

    if hasattr( _stderr_default, "__qualname__" ):
        __qualname__ = _stderr_default.__qualname__

    if hasattr( _stderr_default, "__reduce__" ):
        __reduce__ = _stderr_default.__reduce__

    if hasattr( _stderr_default, "__reduce_ex__" ):
        __reduce_ex__ = _stderr_default.__reduce_ex__

    if hasattr( _stderr_default, "__repr__" ):
        __repr__ = _stderr_default.__repr__

    if hasattr( _stderr_default, "__setattr__" ):
        __setattr__ = _stderr_default.__setattr__

    if hasattr( _stderr_default, "__sizeof__" ):
        __sizeof__ = _stderr_default.__sizeof__

    if hasattr( _stderr_default, "__str__" ):
        __str__ = _stderr_default.__str__

    if hasattr( _stderr_default, "__subclasscheck__" ):
        __subclasscheck__ = _stderr_default.__subclasscheck__

    if hasattr( _stderr_default, "__subclasses__" ):
        __subclasses__ = _stderr_default.__subclasses__

    if hasattr( _stderr_default, "__subclasshook__" ):
        __subclasshook__ = _stderr_default.__subclasshook__

    if hasattr( _stderr_default, "__text_signature__" ):
        __text_signature__ = _stderr_default.__text_signature__

    if hasattr( _stderr_default, "__weakrefoffset__" ):
        __weakrefoffset__ = _stderr_default.__weakrefoffset__

    if hasattr( _stderr_default, "mro" ):
        mro = _stderr_default.mro

    def __init__(self):
        """
            Assures all attributes were statically replaced just above. This should happen in case
            some new attribute is added to the python language.

            This also ignores the only two methods which are not equal, `__init__()` and `__getattribute__()`.
        """
        different_methods = ("__init__", "__getattribute__")
        attributes_to_check = set( dir( object ) + dir( type ) )

        for attribute in attributes_to_check:

            if attribute not in different_methods \
                    and hasattr( _stderr_default, attribute ):

                base_class_attribute = super( _stderr_default_class_type, self ).__getattribute__( attribute )
                target_class_attribute = _stderr_default.__getattribute__( attribute )

                if base_class_attribute != target_class_attribute:
                    sys.stderr.write( "    The base class attribute `%s` is different from the target class:\n%s\n%s\n\n" % (
                            attribute, base_class_attribute, target_class_attribute ) )

    def __getattribute__(self, item):

        if item == 'write':
            return _sys_stderr_write

        try:
            return _stderr_default.__getattribute__( item )

        except AttributeError:
            return super( _stderr_default_class_type, _stderr_default ).__getattribute__( item )


def _do_my_stuff(*args, **kwargs):
    print( "Doing my stuff: %s %s" % ( str( args ), str( kwargs ) ) )


def _sys_stderr_write_hidden(*args, **kwargs):
    _stderr_default.write( *args, **kwargs )
    _do_my_stuff( *args, **kwargs )


try:
    _sys_stderr_write

except NameError:

    def _sys_stderr_write(*args, **kwargs):
        """
            Hides the actual function pointer. This allow the external function
            pointer to be cached while the internal written can be exchanged
            between the standard `sys.stderr.write` and our custom wrapper
            around it.
        """
        _sys_stderr_write_hidden( *args, **kwargs )


do_not_work = StdErrReplamentHidden()
sys.stderr = do_not_work

sys.stderr.write( "do_not_work: " )
sys.stderr.write( "%s\n" % str( do_not_work ) )


