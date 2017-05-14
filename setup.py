# vi: ft=python sw=4 ts=4 et:

'''Get monotonic time in Python.
'''

from __future__ import print_function
from __future__ import unicode_literals

from distutils.core import setup


# A list of classifiers can be found here:
#   http://pypi.python.org/pypi?%3Aaction=list_classifiers
classifiers = '''Natural Language :: English
Development Status :: 4 - Beta
License :: OSI Approved :: MIT License
Programming Language :: Python
Operating System :: MacOS :: MacOS X
Operating System :: POSIX :: Linux
Operating System :: POSIX :: BSD :: FreeBSD
Operating System :: Microsoft :: Windows
'''

import sys

if sys.version_info[0:2] < (2, 3):
    _setup = setup
    def setup(**kwargs):
        if kwargs.has_key('classifiers'):
            del kwargs['classifiers']
        _setup(**kwargs)

doclines = __doc__.split('\n')

setup(name='monotonic_time',
    description=doclines[0],
    long_description='\n'.join(doclines[2:]),
    author='Gavin Beatty',
    author_email='gavinbeatty@gmail.com',
    maintainer='Gavin Beatty',
    maintainer_email='gavinbeatty@gmail.com',
    license = 'http://www.opensource.org/licenses/MIT',
    platforms=['any'],
    classifiers=filter(None, classifiers.split('\n')),
    url='https://github.com/gavinbeatty/python-monotonic-time',
    version='2.0',
    py_modules=['monotonic_time']
)
