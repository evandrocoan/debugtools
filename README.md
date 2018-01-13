
# Python Debug Tools


Basic logger for python on the output form:
```
[main.py] 2018-01-12, 23:34:08:081.722975 DEBUG(1) 3.16e-04 Debugging
[main.py] 2018-01-12, 23:34:08:082.222939 DEBUG(1) 2.80e-04 ...
[main.py] 2018-01-12, 23:34:08:082.222939 DEBUG(1) 2.73e-04 ...
[main.py] 2018-01-12, 23:34:08:082.722902 DEBUG(1) 2.95e-04 Entering on main(0)
[main.py] 2018-01-12, 23:34:08:082.722902 DEBUG(1) 2.79e-04 ( Player ) Creating the player: Player 0
[main.py] 2018-01-12, 23:34:08:083.224058 DEBUG(1) 2.80e-04 ( Player ) Creating the player: Player 1
[main.py] 2018-01-12, 23:34:08:083.724022 DEBUG(1) 2.71e-04 ( Player ) Creating the player: Player 2
[main.py] 2018-01-12, 23:34:08:083.724022 DEBUG(1) 3.13e-04 ( Player ) Creating the player: Player 3
[main.py] 2018-01-12, 23:34:08:084.224939 DEBUG(1) 2.94e-04 ( Player ) Creating the player: Player 4
[main.py] 2018-01-12, 23:34:08:084.224939 DEBUG(1) 2.81e-04 ( StickIntelligence ) Creating the intelligence for 5 players
[main.py] 2018-01-12, 23:34:08:084.724903 DEBUG(1) 2.90e-04 ( StickIntelligence ) Starting the next row of fun...
[main.py] 2018-01-12, 23:34:08:084.724903 DEBUG(1) 2.71e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 2018-01-12, 23:34:08:085.226059 DEBUG(1) 3.29e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 2018-01-12, 23:34:08:085.726023 DEBUG(1) 2.98e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 2018-01-12, 23:34:08:085.726023 DEBUG(1) 2.98e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
[main.py] 2018-01-12, 23:34:08:086.225986 DEBUG(1) 2.78e-04 ( AgentPlayer ) I am a good boy, as long as I am playing.
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
from python_debug_tools.debug_tools import getLogger

imp.reload( python_debug_tools.debug_tools )
from python_debug_tools.debug_tools import getLogger
```




