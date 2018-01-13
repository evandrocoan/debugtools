
# Python Debug Tools


Basic logger for python on the output form:
```
[main.py] 23:34:08:081.722975 3.16e-04 Debugging
[main.py] 23:34:08:082.222939 2.80e-04 ...
[main.py] 23:34:08:082.222939 2.73e-04 ...
[main.py] 23:34:08:082.722902 2.95e-04 Entering on main(0)
[main.py] 23:34:08:082.722902 2.79e-04 ( Player ) Creating the player: Player 0
[main.py] 23:34:08:083.224058 2.80e-04 ( Player ) Creating the player: Player 1
[main.py] 23:34:08:083.724022 2.71e-04 ( Player ) Creating the player: Player 2
[main.py] 23:34:08:083.724022 3.13e-04 ( Player ) Creating the player: Player 3
[main.py] 23:34:08:084.224939 2.94e-04 ( Player ) Creating the player: Player 4
[main.py] 23:34:08:084.224939 2.81e-04 ( StickIntelligence ) Creating the intelligence for 5 players
[main.py] 23:34:08:084.724903 2.90e-04 ( StickIntelligence ) Starting the next row of fun...
[main.py] 23:34:08:084.724903 2.71e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 23:34:08:085.226059 3.29e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 23:34:08:085.726023 2.98e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 23:34:08:085.726023 2.98e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 23:34:08:086.225986 2.78e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
```


To use it:
```python
# Import the debugger
from python_debug_tools import getLogger

# Enable debug messages: (bitwise)
#
# 0   - Disabled debugging.
# 1   - Basic logging messages.
# 2   - AgentPlayer       class' notices.
# 4   - StickIntelligence class' notices.
# 127 - All debugging levels at the same time.
#
log = getLogger( 127, os.path.basename( __file__ ) )

# Later, use `log.log_level = 0` to disable the debugger, or change the level.
log( 1, "Debugging" )
log( 1, "..." )
log( 1, "..." )
```

Or something like:
```python
import os
import sys

def assert_path(module):

    if module not in sys.path:
        sys.path.append( module )

# Import the debug tools
assert_path( os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'PythonDebugTools/all' ) )

# Import the debugger
from python_debug_tools import getLogger

# Enable debug messages: (bitwise)
#
# 0   - Disabled debugging.
# 1   - Basic logging messages.
# 2   - AgentPlayer       class' notices.
# 4   - StickIntelligence class' notices.
# 127 - All debugging levels at the same time.
#
log = getLogger( 127, os.path.basename( __file__ ) )

# Later, use `log.log_level = 0` to disable the debugger, or change the level.
log( 1, "Debugging" )
log( 1, "..." )
log( 1, "..." )
```

If you want to reload the debug tools code on the fly, you can use this to import it:
```
import imp
from python_debug_tools.logger import getLogger

imp.reload( python_debug_tools.logger )
from python_debug_tools.logger import getLogger
```


# License

All files distributed are licensed under this:
```python
# Python Debug Tools, debug help utilities
# Copyright (C) 2017 Evandro Coan <https://github.com/evandrocoan>
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
```

The function `def findCaller(self, stack_info=False)` distributed is licensed under this:
```python
# Copyright 2001-2016 by Vinay Sajip. All Rights Reserved.
#
# Permission to use, copy, modify, and distribute this software and its
# documentation for any purpose and without fee is hereby granted,
# provided that the above copyright notice appear in all copies and that
# both that copyright notice and this permission notice appear in
# supporting documentation, and that the name of Vinay Sajip
# not be used in advertising or publicity pertaining to distribution
# of the software without specific, written prior permission.
# VINAY SAJIP DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE, INCLUDING
# ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL
# VINAY SAJIP BE LIABLE FOR ANY SPECIAL, INDIRECT OR CONSEQUENTIAL DAMAGES OR
# ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER
# IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT
# OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
```

