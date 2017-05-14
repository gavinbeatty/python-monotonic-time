# vi: ft=python sw=4 ts=4 et:

from __future__ import print_function
from __future__ import unicode_literals

from setuptools import setup
from codecs import open
from os import path
import sys

import monotonic_time


# See https://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = '''Natural Language :: English
Development Status :: 4 - Beta
License :: OSI Approved :: MIT License
Programming Language :: Python :: 2
Programming Language :: Python :: 3
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD :: FreeBSD
Operating System :: Microsoft :: Windows
'''

if sys.version_info[0:2] < (2, 3):
    _setup = setup

    def setup(**kwargs):
        kwargs.pop('classifiers', None)
        _setup(**kwargs)


here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='monotonic_time',
    version=monotonic_time.__version__,
    description=monotonic_time.__doc__.split('\n')[0],
    long_description=long_description,
    author='Gavin Beatty',
    author_email='gavinbeatty@gmail.com',
    maintainer='Gavin Beatty',
    maintainer_email='gavinbeatty@gmail.com',
    license='MIT',
    platforms=['any'],
    classifiers=filter(None, classifiers.split('\n')),
    url='https://github.com/gavinbeatty/python-monotonic-time',
    # https://packaging.python.org/en/latest/single_source_version.html
    py_modules=['monotonic_time'],
    keywords='monotonic time clock'.split()
)
