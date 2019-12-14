# Debug Tools

[![Build Status](https://travis-ci.org/evandrocoan/debugtools.svg?branch=master)](https://travis-ci.org/evandrocoan/debugtools)
[![Build status](https://ci.appveyor.com/api/projects/status/github/evandrocoan/debugtools?branch=master&svg=true)](https://ci.appveyor.com/project/evandrocoan/PythonDebugTools/branch/master)
[![Coverage Status](https://coveralls.io/repos/github/evandrocoan/debugtools/badge.svg?branch=HEAD)](https://coveralls.io/github/evandrocoan/debugtools?branch=HEAD)
[![Codacy Badge](https://api.codacy.com/project/badge/Grade/5f3e2cd536b54774b193a1eeef930e3c)](https://www.codacy.com/app/evandrocoan/debugtools?utm_source=github.com&amp;utm_medium=referral&amp;utm_content=evandrocoan/debugtools&amp;utm_campaign=Badge_Grade)
[![Latest Release](https://img.shields.io/github/tag/evandrocoan/debugtools.svg?label=version)](https://github.com/evandrocoan/debugtools/releases)
[![PyPi Versions](https://img.shields.io/pypi/pyversions/debug_tools.svg)](https://pypi.python.org/pypi/debug_tools)

Basic logger for Python `logging` module.


___
## Usage

```
pip install debug_tools
```

Or clone this repository locally by running the commands:
```
git clone https://github.com/evandrocoan/debugtools
cd debugtools
```
Then, run `python setup.py install` or `python setup.py develop` to install it on development mode.


```python
from debug_tools import getLogger

# Enable debug messages: (bitwise)
# 0   - Disabled debugging.
# 1   - Basic logging messages.
# 2   - AgentPlayer       class' notices.
# 4   - StickIntelligence class' notices.
# 127 - All debugging levels at the same time.
log = getLogger( 127, __name__ )
log( 1, "Debugging" )
```


### Cleaning the log file every start up

If you are logging the debug output to a file and you would like to clean/erase all the log file contents,
every time you re-create the logger,
you need first to unlock the log file lock, otherwise,
the file contents are not going to be erased.

To unlock your log file,
you just need to call `log.setup("")`,
with an empty string before creating a new logger.

On Sublime Text, this could be done with te following:
```python
from debug_tools import getLogger
log = getLogger(debug_enabled, "wrap_plus", "wrapplus.txt", mode='w')

def plugin_unloaded():
    log.delete()
```


### Dynamically Reloading It

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


### Using file logger configuration

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
            "portalockerfile",
            "concurrentloghandler",
            "debugtools"
        ]
    },
    "*": {
        "*": [
            "portalockerfile",
            "concurrentloghandler",
            "debugtools"
        ]
    }
}
```


### Update estimated_time_left from upstream

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

