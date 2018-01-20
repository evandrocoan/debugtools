#!/usr/bin/env python

# https://setuptools.readthedocs.io/en/latest/setuptools.html
from setuptools import setup

#
# Release process
#
# Setup:
# vim ~/.pypirc
# .pypirc file contents
#
# [distutils]
# index-servers =
#   pypi
#   pypitest
#
# [pypi]
# username: YOUR_USERNAME_HERE
# password: YOUR_PASSWORD_HERE
#
# [pypitest]
# username: YOUR_USERNAME_HERE
# password: YOUR_PASSWORD_HERE
#
# Run this to build the `dist/PACKAGE_NAME-xxx.tar.gz` file
#     python setup.py sdist
#
# Run this to build & upload it to `pypi`:
#     python setup.py sdist upload -r pypi
#

setup \
(
      name='python_debug_tools',
      version = '1.0.2',
      description = 'Python Distribution Logger, Debugger and Utilities',
      author = 'Evandro Coan',
      license = "GPLv3",
      url = 'https://github.com/evandrocoan/PythonDebugTools',
      package_dir = {'': 'all'},
      packages = ['python_debug_tools'],
      long_description = open('README.md').read(),
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
          'Topic :: Software Development :: Libraries :: Python Modules',
      ],
)

