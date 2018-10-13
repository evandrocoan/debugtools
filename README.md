# Python Debug Tools

[![Build Status](https://travis-ci.org/evandrocoan/DebugTools.svg?branch=master)](https://travis-ci.org/evandrocoan/DebugTools)
[![Build status](https://ci.appveyor.com/api/projects/status/github/evandrocoan/DebugTools?branch=master&svg=true)](https://ci.appveyor.com/project/evandrocoan/PythonDebugTools/branch/master)
[![codecov](https://codecov.io/gh/evandrocoan/DebugTools/branch/master/graph/badge.svg)](https://codecov.io/gh/evandrocoan/DebugTools)
[![Coverage Status](https://coveralls.io/repos/github/evandrocoan/DebugTools/badge.svg?branch=HEAD)](https://coveralls.io/github/evandrocoan/DebugTools?branch=HEAD)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f3e2cd536b54774b193a1eeef930e3c)](https://www.codacy.com/app/evandrocoan/DebugTools?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=evandrocoan/DebugTools&amp;utm_campaign=Badge_Grade)
[![Latest Release](https://img.shields.io/github/tag/evandrocoan/DebugTools.svg?label=version)](https://github.com/evandrocoan/DebugTools/releases)
[![PyPi Versions](https://img.shields.io/pypi/pyversions/debug_tools.svg)](https://pypi.python.org/pypi/debug_tools)

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

See also the example on [tests/manual_tests.py](tests/manual_tests.py):
```
reloading plugin DebugTools.tests.manual_tests
reloading plugin DebugTools.logger
[DebugTools.tests.manual_tests] 16:31:26:638.928890 2.19e-04 <module>:13 My logging
[DebugTools.tests.manual_tests] 16:31:26:639.429092 4.90e-04 <module>:14 A warning
[DebugTools.tests.manual_tests] 16:31:26:639.930010 4.77e-04 <module>:15 A debugging

[DebugTools.tests.manual_tests] 16:31:26:640.930891 3.87e-04 DEBUG(1) Bitwise
[DebugTools.tests.manual_tests] 16:31:26:641.431093 4.62e-04 DEBUG(8) Bitwise
[DebugTools.tests.manual_tests] 16:31:26:641.431093 3.04e-04 WARNING Warn
[DebugTools.tests.manual_tests] 16:31:26:641.931057 2.96e-04 INFO Info
[DebugTools.tests.manual_tests] 16:31:26:642.431974 2.80e-04 DEBUG Debug

[DebugTools.tests.manual_tests] 2018-01-13 16:31:26:642.931938 2.47e-04 function_name:18 Bitwise
[DebugTools.tests.manual_tests] 2018-01-13 16:31:26:642.931938 2.88e-04 function_name:19 Bitwise
[DebugTools.tests.manual_tests] 2018-01-13 16:31:26:643.431902 3.04e-04 function_name:20 Warn
[DebugTools.tests.manual_tests] 2018-01-13 16:31:26:643.431902 2.85e-04 function_name:21 Info
[DebugTools.tests.manual_tests] 2018-01-13 16:31:26:643.933058 2.99e-04 function_name:22 Debug
```


___
## Usage

```
pip install debug_tools
```

Or clone this repository locally by running the commands:
```
git clone https://github.com/evandrocoan/DebugTools
cd DebugTools
```
Then `python setup.py install` or `python setup.py develop` to install it on development mode.


```python
# Import the debugger
from debug_tools import getLogger

# Enable debug messages: (bitwise)
#
# 0   - Disabled debugging.
# 1   - Basic logging messages.
# 2   - AgentPlayer       class' notices.
# 4   - StickIntelligence class' notices.
# 127 - All debugging levels at the same time.
log = getLogger( 127, __name__ )

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
assert_path( os.path.join( os.path.dirname( os.path.realpath( __file__ ) ), 'DebugTools', 'all' ) )

# Import the debugger
from debug_tools import getLogger

# Enable debug messages: (bitwise)
#
# 0   - Disabled debugging.
# 1   - Basic logging messages.
# 2   - AgentPlayer       class' notices.
# 4   - StickIntelligence class' notices.
# 127 - All debugging levels at the same time.
#
# log = getLogger( 127, os.path.basename( __file__ ) )
log = getLogger( 127, __name__ )

# Later, use `log.log_level = 0` to disable the debugger, or change the level.
log( 1, "Debugging" )
log( 1, "..." )
log( 1, "..." )
```

If you want to reload the debug tools code on the fly, you can use this to import it:
```python
import imp
import debug_tools.logger

imp.reload( debug_tools.logger )
from debug_tools.logger import Debugger
from debug_tools.logger import getLogger

Debugger.deleteAllLoggers()
log = getLogger(1, "LSP")
```

If you want to load the logger configuration from a file, you need to replace the standard logging
module class with this one:
```
import logging
import debug_tools

if log_config:

    with open(log_config, 'r') as f:
        logging.Logger.manager = debug_tools.Debugger.manager
        logging.Logger.manager.setLoggerClass( debug_tools.Debugger )

        logging.config.dictConfig(json.load(f))
```


## Sublime Text Dependency

To use this as a Package Control Dependency https://packagecontrol.io/docs/dependencies create
this `dependencies.json` file on the root of your Package:
```json
{
    "windows": {
        ">3000": [
            "python-pywin32",
            "PortalockerFiles",
            "ConcurrentLogHandler",
            "DebugTools"
        ]
    },
    "*": {
        "*": [
            "PortalockerFiles",
            "ConcurrentLogHandler",
            "DebugTools"
        ]
    }
}
```


## Update estimated_time_left from upstream

To update the subtree `all/debug_tools/estimated_time_left`,
from upstream updates you can use the command:
```shell
git subtree pull --prefix=all/debug_tools/estimated_time_left https://github.com/evandrocoan/EstimatedTimeLeft master
```

To send updates back to the upstream, use the following command:
```shell
git subtree push --prefix=all/debug_tools/estimated_time_left https://github.com/evandrocoan/EstimatedTimeLeft master
```


# License

See the file [LICENSE.txt](LICENSE.txt)

