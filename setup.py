#! /usr/bin/env python
# -*- coding: utf-8 -*-

try:
    import sublime_api

except ImportError:
    #
    # Release process setup see:
    # https://github.com/pypa/twine
    #
    # To setup password cache:
    # sudo apt-get install python3-dbus
    # pip3 install --user keyring
    # python3 -m keyring set https://test.pypi.org/legacy/ your-username
    #
    # Run this to build the `dist/PACKAGE_NAME-xxx.tar.gz` file
    #     rm -rf ./dist && python3 setup.py sdist
    #
    # Run this to build & upload it to `pypi`, type your account name when prompted.
    #     twine upload dist/*
    #
    # All in one command:
    #     rm -rf ./dist && python3 setup.py sdist && twine upload dist/*
    #
    import re
    import sys
    import codecs

    try:
        # https://stackoverflow.com/questions/2058802/how-can-i-get-the-version-defined-in-setup-py-setuptools-in-my-package
        filepath = 'all/debug_tools/version.py'

        with open( filepath, 'r' ) as file:
            __version__ ,= re.findall('__version__ = "(.*)"', file.read())

    except Exception as error:
        __version__ = "0.0.1"
        sys.stderr.write( "Warning: Could not open '%s' due %s" % ( filepath, error ) )

    try:
        # https://stackoverflow.com/questions/30700166/python-open-file-error
        with codecs.open( "README.md", 'r', errors='ignore' ) as file:
            readme_contents = file.read()

    except Exception as error:
        readme_contents = ""
        sys.stderr.write( "Warning: Could not open README.md due %s" % error )

    # https://setuptools.readthedocs.io/en/latest/setuptools.html
    from distutils.version import StrictVersion
    from setuptools import setup
    from setuptools import __version__ as setuptools_version

    install_requires=[
    ]

    # https://setuptools.readthedocs.io/en/latest/history.html
    required_setup_tools = '20.5'

    # https://stackoverflow.com/questions/48048745/setup-py-require-a-recent-version-of-setuptools-before-trying-to-install
    if StrictVersion( setuptools_version ) < StrictVersion( required_setup_tools ):
        sys.stderr.write( " Warning: Your setuptools version '%s' is not fully support this package.\n"
                "Please upgrade your setuptools to '%s' or newer and repeat the installation.\n"
                "     pip install setuptools --upgrade\n"
                "     pip3 install setuptools --upgrade\n" % (
                setuptools_version, required_setup_tools )
            )
        extras_require = {}

    else:
        # To install use: pip install -e .[full]
        # To install use: pip install -e debug_tools[full]
        # To install use: pip install -e debug_tools debug_tools[full]
        extras_require = {
            'full': [
                "natsort",
                "diff-match-patch",
                'portalocker; python_version>"3.4"',
                'concurrent-log-handler; python_version>"3.4"',
            ],
            'diff': [
                "diff-match-patch",
            ],
            'sort': [
                "natsort",
            ],
            'lock': [
                'portalocker; python_version>"3.4"',
                'concurrent-log-handler; python_version>"3.4"',
            ],
        }

        if sys.platform.startswith("win") or sys.platform.startswith("cyg"):
            extras_require['full'].append('pypiwin32;python_version>"3.4"')
            extras_require['lock'].append('pypiwin32;python_version>"3.4"')

    setup \
    (
        name='debug_tools',
        version = __version__,
        description = 'Python Distribution Logger, Debugger and Utilities',
        author = 'Evandro Coan',
        license = "GPLv3",
        url = 'https://github.com/evandrocoan/debug_tools',

        package_dir = {
            '': 'all'
        },

        packages = [
            'debug_tools',
        ],

        data_files = [
            ("", ["LICENSE.txt"]),
        ],

        extras_require = extras_require,
        install_requires = install_requires,
        long_description = readme_contents,
        long_description_content_type='text/markdown',
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
            'Operating System :: OS Independent',
            'Programming Language :: Python',
            'Programming Language :: Python :: 2',
            'Programming Language :: Python :: 2.7',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4',
            'Programming Language :: Python :: 3.5',
            'Programming Language :: Python :: 3.6',
            'Programming Language :: Python :: 3.7',
            'Topic :: Software Development :: Libraries :: Python Modules',
        ],
    )

